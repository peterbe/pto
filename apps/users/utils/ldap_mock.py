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

import ldap
from django.conf import settings


class MockLDAP:  # pragma: no cover
    def __init__(self, search_result, credentials=None):
        self.search_result = search_result
        self.credentials = credentials

    def search_s(self, search, scope, filter=None, attrs=None):
        #print "INPUT", (search, filter)
        o = self._search_s(search, scope, filter=filter, attrs=attrs)
        #print "OUTPUT", o
        return o

    def _search_s(self, search, scope, filter=None, attrs=None):
        if search in self.search_result:
            return self.search_result[search]

        if filter:
            #print "FILTER", repr(filter)
            #print "KEYS"
            #print self.search_result.keys()
            try:
                return self.search_result[filter]
            except KeyError:
                pass
        return []

    def simple_bind_s(self, dn, password):
        try:
            o = self._simple_bind_s(dn, password)
        except:
            raise

    def _simple_bind_s(self, dn, password):
        if self.credentials is None:
            # password check passed
            return
        if dn == getattr(settings, 'AUTH_LDAP_BIND_DN', None):
            # sure, pretend we can connect successfully
            return
        try:
            if self.credentials[dn] != password:
                raise ldap.INVALID_CREDENTIALS
        except KeyError:
            raise ldap.UNWILLING_TO_PERFORM

    def void(self, *args, **kwargs):
        pass

    set_option = unbind_s = start_tls_s = void
