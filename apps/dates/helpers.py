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

import urllib
import urlparse

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse

import jinja2
from jingo import register


def urlencode(items):
    """A Unicode-safe URLencoder."""
    try:
        return urllib.urlencode(items)
    except UnicodeEncodeError:
        return urllib.urlencode([(k, smart_str(v)) for k, v in items])


def urlparams(url_, hash=None, **query):
    """
    Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = urlencode([(k, v) for k, v in query_dict.items()
                             if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()


@register.function
@jinja2.contextfunction
def truncatewords(context, string, length):
    if len(string) > length:
        string = string[:length - 3] + '...'
    return string


@register.function
@jinja2.contextfunction
def media(context, url, key='MEDIA_URL'):
    """Get a MEDIA_URL link with a cache buster querystring."""
    if url.endswith('.js'):
        build = context['BUILD_ID_JS']
    elif url.endswith('.css'):
        build = context['BUILD_ID_CSS']
    else:
        #build = context['BUILD_ID_IMG']
        build = context['BUILD_ID_JS']
    return context[key] + urlparams(url, b=build)


@register.function
@jinja2.contextfunction
def static(context, url):
    """Get a STATIC_URL link with a cache buster querystring."""
    return media(context, url, 'STATIC_URL')


@register.function
@jinja2.contextfunction
def entry_to_list_url(context, entry):
    url = reverse('dates.list')
    values = {'name': entry.user.email,
              'date_from': entry.start.strftime('%d %B %Y'),
              'date_to': entry.end.strftime('%d %B %Y'),
              }
    values_encoded = urllib.urlencode(values)
    return '%s?%s' % (url, values_encoded)


@register.function
@jinja2.contextfunction
def full_name_form(context, user, avoid_email=False):
    if user is None:
        return ''
    elif (isinstance(user, dict)
        and 'sn' in user
        and 'givenName' in user
        and 'mail' in user):
        name = ('%s %s' % (user['givenName'],
                           user['sn'])).strip()
        if not name:
            name = user['cn']
        email = user['mail']
    elif isinstance(user, User):
        name = ('%s %s' % (user.first_name,
                           user.last_name)).strip()
        if not name:
            name = user.username
        email = user.email
    else:
        assert isinstance(user, basestring)
        if '@' in user:
            email = user
            name = None
        else:
            email = None
            name = user

    if name and email and not avoid_email:
        return '%s <%s>' % (name, email)
    elif name:
        return name
    else:
        return email


@register.function
@jinja2.contextfunction
def format_date(context, date, format=None, shorter=False):
    if format is None:
        format = settings.DEFAULT_DATE_FORMAT
    if shorter:
        format = format.replace('%B', '%b')
        format = format.replace('%A', '%a')
    return date.strftime(format)
