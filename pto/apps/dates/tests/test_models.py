# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from django.contrib.auth.models import User
from pto.apps.dates.models import (
  Entry,
  Hours,
  BlacklistedUser,
  FollowingUser,
  FollowingIntegrityError,
  BlacklistIntegityError,
  UserKey
)
from nose.tools import eq_, ok_
from test_utils import TestCase


class ModelsTest(TestCase):

    def test_cascade_delete_entry(self):
        user = User.objects.create_user(
          'mortal', 'mortal', password='secret'
        )
        entry = Entry.objects.create(
          user=user,
          start=datetime.date.today(),
          end=datetime.date.today(),
          total_hours=8
        )

        Hours.objects.create(
          entry=entry,
          hours=8,
          date=datetime.date.today()
        )

        user2 = User.objects.create_user(
          'other', 'other@test.com', password='secret'
        )
        entry2 = Entry.objects.create(
          user=user2,
          start=datetime.date.today(),
          end=datetime.date.today(),
          total_hours=4
        )

        Hours.objects.create(
          entry=entry2,
          hours=4,
          date=datetime.date.today()
        )

        eq_(Hours.objects.all().count(), 2)
        entry.delete()
        eq_(Hours.objects.all().count(), 1)

    def test_following_blacklisted_integrity(self):
        peter = User.objects.create(username='peter')
        axel = User.objects.create(username='axel')

        assert not BlacklistedUser.objects.filter(observer=peter)
        assert not FollowingUser.objects.filter(follower=peter)

        BlacklistedUser.objects.create(
          observer=peter,
          observable=axel
        )
        assert BlacklistedUser.objects.filter(observer=peter)
        assert not FollowingUser.objects.filter(follower=peter)

        FollowingUser.objects.create(
          follower=peter,
          following=axel
        )
        ok_(not BlacklistedUser.objects.filter(observer=peter))
        ok_(FollowingUser.objects.filter(follower=peter))

        # change back
        BlacklistedUser.objects.create(
          observer=peter,
          observable=axel
        )
        ok_(BlacklistedUser.objects.filter(observer=peter))
        ok_(not FollowingUser.objects.filter(follower=peter))

    def test_self_following_integrity_check(self):
        peter = User.objects.create(username='peter')

        self.assertRaises(FollowingIntegrityError,
                          FollowingUser.objects.create,
                          follower=peter,
                          following=peter
        )

    def test_self_blacklisting_integrity_check(self):
        peter = User.objects.create(username='peter')

        self.assertRaises(BlacklistIntegityError,
                          BlacklistedUser.objects.create,
                          observer=peter,
                          observable=peter
        )

    def test_user_keys(self):
        peter = User.objects.create(username='peter')
        uk = UserKey.objects.create(user=peter)

        ok_(uk.add_date)
        ok_(uk.key)
        eq_(len(uk.key), UserKey.KEY_LENGTH)

        peter2 = User.objects.create(username='peter2')
        uk2 = UserKey.objects.create(user=peter2)
        ok_(uk.key != uk2.key)

        eq_(UserKey.objects.all().count(), 2)

        peter.delete()
        eq_(UserKey.objects.all().count(), 1)

    def test_user_keys_uniqueness(self):
        peter = User.objects.create(username='peter')
        keys = set()
        for i in range(1000):
            uk = UserKey.objects.create(user=peter)
            if uk.key in keys:
                raise AssertionError('same key reused')
            keys.add(uk.key)
