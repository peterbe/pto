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
# The Original Code is Mozilla Sheriff Duty.
#
# The Initial Developer of the Original Code is Mozilla Corporation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#    Peter Bengtsson, <peterbe@mozilla.com>
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

import logging
from django import http
from dates.decorators import json_view
from users.models import UserProfile, User
from users.utils import ldap_lookup


@json_view
def cities(request):
    if not request.user.is_authenticated():
        return http.HttpResponseForbidden('Must be logged in')
    data = []
    term = request.GET.get('term')
    qs = UserProfile.objects.exclude(city='')
    if term:
        qs = qs.filter(city__istartswith=term)
    for each in (qs
                     .values('city')
                     .distinct('city')
                     .order_by('city')):
        city = each['city']
        data.append(city)
    return data

@json_view
def users(request, known_only=False):
    if not request.user.is_authenticated():
        return http.HttpResponseForbidden('Must be logged in')
    query = request.GET.get('term').strip()
    if len(query) < 2:
        return []

    results = []
    # I chose a limit of 30 because there are about 20+ 'peter'
    # something in mozilla
    for each in ldap_lookup.search_users(query, 30, autocomplete=True):
        if not each.get('givenName'):
            logging.warn("Skipping LDAP entry %s" % each)
            continue
        if known_only:
            if not User.objects.filter(email__iexact=each['mail']).exists():
                continue
        full_name_and_email = '%s %s <%s>' % (each['givenName'],
                                              each['sn'],
                                              each['mail'])
        result = {'id': each['uid'],
                  'label': full_name_and_email,
                  'value': full_name_and_email}
        results.append(result)
    return results
