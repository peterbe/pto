# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
# 
# The Initial Developer of the Original Code is Mozilla Corporation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
# 
# Contributor(s):
#   Peter Bengtsson <peterbe@mozilla.com>
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

import re
import ldap
from ldap.filter import filter_format
from django.utils.encoding import smart_unicode
from django.conf import settings
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django_auth_ldap.config import LDAPSearch


def account_wrap_search_filter(search_filter):
    if not (search_filter.startswith('(') and search_filter.endswith(')')):
        search_filter = '(%s)' % search_filter
    return '(&(objectClass=inetOrgPerson)(mail=*)%s)' % (search_filter,)


def _valid_email(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False

def fetch_user_details(email, force_refresh=False):
    cache_key = 'ldap_peeps_%s' % hash(email)
    if not force_refresh:
        result = cache.get(cache_key)
        if result is not None:
            return result

    results = search_users(email, 1)
    if results:
        result = results[0]
        _expand_result(result)
        cache.set(cache_key, result, 60 * 60)
    else:
        result = {}
        # tell the cache to not bother again, for a while
        cache.set(cache_key, result, 60)

    return result


def search_users(query, limit, autocomplete=False):
    connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    if limit > 0:
        connection.set_option(ldap.OPT_SIZELIMIT, limit)
    connection.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                             settings.AUTH_LDAP_BIND_PASSWORD)
    if autocomplete:
        filter_elems = []
        if query.startswith(':'):
            searches = {'uid': query[1:]}
        else:
            searches = {'givenName': query, 'sn': query, 'mail': query}
            if ' ' in query:
                # e.g. 'Peter b' or 'laura toms'
                searches['cn'] = query
        for key, value in searches.items():
            assert value
            filter_elems.append(filter_format('(%s=%s*)',
                                              (key, value)))
        search_filter = ''.join(filter_elems)
        if len(filter_elems) > 1:
            search_filter = '(|%s)' % search_filter
    else:
        if '@' in query and _valid_email(query):
            search_filter = filter_format("(mail=%s)", (query, ))
        elif query.startswith(':'):
            search_filter = filter_format("(uid=%s)", (query[1:], ))
        else:
            search_filter = filter_format("(cn=*%s*)", (query, ))
    attrs = ['cn', 'sn', 'mail', 'givenName', 'uid', 'objectClass']
    search_filter = account_wrap_search_filter(search_filter)

    rs = connection.search_s("dc=mozilla", ldap.SCOPE_SUBTREE,
                            search_filter,
                            attrs)
    results = []
    for each in rs:
        result = each[1]
        _expand_result(result)
        results.append(result)
        if len(results) >= limit:
            break

    return results

def _expand_result(result):
    """
    Turn
      {'givenName': ['Peter'], ...
    Into
      {'givenName': u'Peter', ...
    """
    for key, value in result.items():
        if isinstance(value, list):
            if len(value) == 1:
                value = smart_unicode(value[0])
            elif not value:
                value = u''
            else:
                value = [smart_unicode(x) for x in value]
            result[key] = value
