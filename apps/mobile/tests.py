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

import datetime
from urlparse import urlparse
from nose.tools import eq_, ok_
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from dates.tests.test_views import ViewsTest as BaseViewsTest
from dates.models import Entry


class MobileViewsTest(BaseViewsTest):

    def _login(self):
        peter = User.objects.create(
          username='peter',
          email='pbengtsson@mozilla.com',
          first_name='Peter',
          last_name='Bengtsson',
        )
        peter.set_password('secret')
        peter.save()
        assert self.client.login(username='peter', password='secret')

    def test_home(self):
        url = reverse('mobile.home')
        response = self.client.get(url)
        eq_(response.status_code, 302)
        path = urlparse(response['location']).path
        eq_(path, settings.LOGIN_URL)

        peter = User.objects.create(
          username='peter',
          email='pbengtsson@mozilla.com',
          first_name='Peter',
          last_name='Bengtsson',
        )
        peter.set_password('secret')
        peter.save()

        assert self.client.login(username='peter', password='secret')

        url = reverse('mobile.home')
        response = self.client.get(url)
        eq_(response.status_code, 200)

    def test_right_now_json(self):
        url = reverse('mobile.right_now')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        ok_(json.loads(response.content)['error'])

        bobby = User.objects.create_user(
          'bobby', 'bobby@mozilla.com',
        )
        freddy = User.objects.create_user(
          'freddy', 'freddy@mozilla.com',
        )
        dicky = User.objects.create_user(
          'dicky', 'dicky@mozilla.com',
        )
        harry = User.objects.create_user(
          'harry', 'harry@mozilla.com',
        )

        today = datetime.date.today()

        Entry.objects.create(
          user=bobby,
          total_hours=16,
          start=today - datetime.timedelta(days=2),
          end=today - datetime.timedelta(days=1),
        )

        Entry.objects.create(
          user=freddy,
          total_hours=16,
          start=today - datetime.timedelta(days=1),
          end=today,
        )

        Entry.objects.create(
          user=dicky,
          total_hours=4,
          start=today,
          end=today,
        )

        Entry.objects.create(
          user=harry,
          total_hours=16,
          start=today + datetime.timedelta(days=1),
          end=today + datetime.timedelta(days=2),
        )

        self._login()
        response = self.client.get(url)
        eq_(response.status_code, 200)
        struct = json.loads(response.content)
        eq_(len(struct['now']), 2)
        eq_(len(struct['upcoming']), 1)
        names = [x['name'] for x in struct['now']]
        ok_('dicky' in names[0])
        ok_('freddy' in names[1])
        names = [x['name'] for x in struct['upcoming']]
        ok_('harry' in names[0])

    def test_left_json(self):
        pass

    def test_notify(self):
        pass

    def test_hours(self):
        pass

    def test_hours_json(self):
        pass

    def test_settings_json(self):
        pass

    def test_save_settings(self):
        pass

    def test_exit_mobile(self):
        pass
