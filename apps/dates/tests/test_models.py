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
from django.contrib.auth.models import User
from django.test import TestCase
from dates.models import (Entry, Hours, BlacklistedUser, FollowingUser,
                          FollowingIntegrityError,
                          BlacklistIntegityError)
from nose.tools import eq_, ok_


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
