# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from django.contrib.auth.models import User
from pto.apps.dates.models import (
  Entry,
  Hours
)

class ExtraTestCaseMixin(object):

    def _login(self, user=None):
        if not user:
            user = User.objects.create(
              username='peter',
              email='pbengtsson@mozilla.com',
              first_name='Peter',
              last_name='Bengtsson',
            )
        user.set_password('secret')
        user.save()
        assert self.client.login(username=user.username, password='secret')
        return user

    def _create_hr_manager(self, username='jill', email='jill@mozilla.com'):
        user = User.objects.create(
          username=username,
          email=email
        )
        profile = user.get_profile()
        profile.hr_manager = True
        profile.save()
        return user

    def _create_entry_hours(self, entry, *hours):
        date = entry.start
        i = 0
        while date <= entry.end:
            try:
                h = hours[i]
            except IndexError:
                h = 8
            Hours.objects.create(
              entry=entry,
              date=date,
              hours=h,
            )
            i += 1
            date += datetime.timedelta(days=1)
