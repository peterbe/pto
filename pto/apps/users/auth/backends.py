# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import re
import ldap
from ldap.filter import filter_format
from django.contrib.auth.models import User
from django_auth_ldap.backend import LDAPBackend


class MozillaLDAPBackend(LDAPBackend):
    """Overriding this class so that I can transform emails to usernames.

    At Mozilla we use email addresses as the username but in django I want,
    for example:
        INPUT:
            username -> pbengtsson@mozilla.com
        OUTPUT:
            username -> pbengtsson
            email -> pbengtsson@mozilla.com

    I can map (in settings.AUTH_LDAP_USER_ATTR_MAP):
        'username' -> 'uid'
        and
        'email -> 'mail

    But that means that the second time a user logs in, it's not going to
    find a username that is 'pbengtsson@mozilla.com' so it'll go ahead and
    create it again and you'll end up with duplicates once the attribute
    conversion is done.

    The other thing that this backend accomplishes is to change username
    entirely. Suppose, for example, that your mozilla LDAP email is
    'pbengtsson@mozilla.com' but you prefer your own custom alias of
    'peterbe'. What it does then, is looking at existing users that match
    the *email address* and returns the username for that one.
    """

    supports_inactive_user = True


    def get_or_create_user(self, username, ldap_user):
        """
        This must return a (User, created) 2-tuple for the given LDAP user.
        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP attributes.

        Note: Be careful with exceptions here because many of them are swallowed
        but django's aweful authentication backends framework. Many exceptions
        are treated as if the authentication failed as opposed to genuine python
        typos and bugs.
        """
        email = username
        if '@' not in email:
            email = '%s@mozilla.com' % username

        # HACK ATTACK!
        # To be able to look up additional protected attributes such as
        # 'manager' we can't use the binduser connection (the bound one) so
        # we have to use the connection made with the user's password (the NOT
        # bound one).
        # Relying on a private method sucks horse but it's the only way to use
        # django-auth-ldap for additional details without having to save the
        # password or maintain a dedicated account (with password in settings)
        # for these kinds of lookups.
        conn = ldap_user._get_connection()

        search_filter = filter_format("(mail=%s)", (email, ))
        # the full list of attribute (for peterbe in this example) is:
        #  ['description',
        #   'physicalDeliveryOfficeName',
        #   'bugzillaEmail',
        #   'employeeType',
        #   'uid',
        #   'ntPassword',
        #   'objectClass',
        #   'title',
        #   'userPassword',
        #   'jpegPhoto',
        #   'lmPassword',
        #   'mobile',
        #   'manager',
        #   'other',
        #   'im',
        #   'sn',
        #   'emailAlias',
        #   'mail',
        #   'rid',
        #   'givenName',
        #   'cn']
        attrs = ['manager', 'physicalDeliveryOfficeName']
        rs = conn.search_s("dc=mozilla", ldap.SCOPE_SUBTREE, search_filter, attrs)
        extra_user_attrs = {}
        ldap_attrs = None
        if rs:
            if rs[0][1].get('manager'):
                manager = rs[0][1]['manager']
                manager = self._clean_manager_attr(manager[0])
                extra_user_attrs['manager'] = [manager]

            if rs[0][1].get('physicalDeliveryOfficeName'):
                extra_user_attrs['physicalDeliveryOfficeName'] = \
                  rs[0][1]['physicalDeliveryOfficeName']

            if extra_user_attrs:
                # at this point, ldap_user.attrs causes the creation of a
                # new bound connection.
                #ldap_attrs = ldap_user.attrs
                if isinstance(ldap_user.attrs, dict):
                    ldap_user.attrs.update(extra_user_attrs)

        # users on this site can't change their email but they can change their
        # username
        if isinstance(ldap_user.attrs, dict) and ldap_user.attrs.get('mail'):
            for user in (User.objects
              .filter(email__iexact=ldap_user.attrs.get('mail')[0])):
                return (user, False)

        # use the default from django-auth-ldap
        user = User.objects.get_or_create(
           username__iexact=username,
           defaults={'username': username.lower()}
        )
        return user

    def _clean_manager_attr(self, value):
        """most likely it's something lie this:
            'mail=foo@mozilla.com,o=com,dc=mozilla'
        Then return just foo@mozilla.com
        """
        regex = re.compile('mail=([^,]+)')
        if regex.findall(value):
            return regex.findall(value)[0]
        return value

    def ldap_to_django_username(self, username):
        """Allow users to use a different username"""
        try:
            return User.objects.get(email=username).username
        except User.DoesNotExist:
            return username.split('@')[0]
