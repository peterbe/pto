# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from nose.tools import eq_, ok_
from test_utils import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from pto.apps.dates.models import (
    BlacklistedUser,
    FollowingUser,
    Entry
)
from pto.apps.dates.data import (
    get_minions,
    get_taken_info,
    get_observed_users,
    get_observing_users
)
from .base import ExtraTestCaseMixin


def ieq_(seq1, seq2):
    return eq_(sorted(seq1, key=lambda u: u.id),
               sorted(seq2, key=lambda u: u.id))

_THIS_YEAR = datetime.date.today().year


class DataTestCase(TestCase, ExtraTestCaseMixin):

    def test_get_taken_info(self):
        user = User.objects.create(username='bob')

        def function():
            return get_taken_info(user)

        result = function()
        eq_(result['taken'], '0 days')
        ok_(not result.get('unrecognized_country'))
        ok_(not result.get('country_total'))

        profile = user.get_profile()
        profile.country = 'US'
        profile.save()
        result = function()
        ok_(not result.get('unrecognized_country'))
        ok_(result.get('country_totals'))
        ok_(result.get('country'), 'US')

        profile.country = 'New Zealand'
        profile.save()
        result = function()
        ok_(result.get('unrecognized_country'))
        ok_(not result.get('country_totals'))
        ok_(result.get('country'), 'New Zealand')

        date = datetime.date(_THIS_YEAR, 11, 23)
        entry = Entry.objects.create(
            user=user,
            start=date,
            end=date,
            total_hours=settings.WORK_DAY,
        )
        self._create_entry_hours(entry)

        result = function()
        eq_(result['taken'], '1 day')

        entry.total_hours = settings.WORK_DAY / 2
        entry.save()
        result = function()
        eq_(result['taken'], '%s hours' % (settings.WORK_DAY / 2))

        one_week = datetime.timedelta(days=7)
        entry = Entry.objects.create(
            user=user,
            start=date + one_week,
            end=date + one_week,
            total_hours=settings.WORK_DAY,
        )
        self._create_entry_hours(entry)

        result = function()
        eq_(result['taken'], '1.5 days')

        entry = Entry.objects.create(
            user=user,
            start=date + one_week * 2,
            end=date + one_week * 2,
            total_hours=settings.WORK_DAY / 2,
        )
        self._create_entry_hours(entry, 4)

        result = function()
        eq_(result['taken'], '2 days')

        entry = Entry.objects.create(
            user=user,
            start=date + one_week * 3,
            end=date + one_week * 5,
            total_hours=settings.WORK_DAY * 14,
        )
        self._create_entry_hours(entry)

        result = function()
        eq_(result['taken'], '16 days')

    def test_get_minions(self):
        gary = User.objects.create_user(
            'gary', 'gary@mozilla.com'
        )

        todd = User.objects.create_user(
            'todd', 'todd@mozilla.com',
        )
        profile = todd.get_profile()
        profile.manager = gary.email
        profile.save()

        mike = User.objects.create_user(
            'mike', 'mike@mozilla.com',
        )
        profile = mike.get_profile()
        profile.manager = todd.email
        profile.save()

        laura = User.objects.create_user(
            'laura', 'laura@mozilla.com',
        )
        profile = laura.get_profile()
        profile.manager = mike.email
        profile.save()

        peter = User.objects.create_user(
            'peter', 'peter@mozilla.com',
        )
        profile = peter.get_profile()
        profile.manager = laura.email
        profile.save()

        users = get_minions(gary, max_depth=1)
        eq_(users, [todd])

        users = get_minions(gary, max_depth=2)
        eq_(users, [todd, mike])

        users = get_minions(gary, max_depth=3)
        eq_(users, [todd, mike, laura])

        users = get_minions(gary, max_depth=4)
        eq_(users, [todd, mike, laura, peter])

        users = get_minions(gary, max_depth=10)
        eq_(users, [todd, mike, laura, peter])

        # from todd's perspective
        users = get_minions(todd, max_depth=1)
        eq_(users, [mike])

        users = get_minions(todd, max_depth=2)
        eq_(users, [mike, laura])

        users = get_minions(todd, max_depth=3)
        eq_(users, [mike, laura, peter])

        users = get_minions(todd, max_depth=10)
        eq_(users, [mike, laura, peter])

        # from laura's perspective
        users = get_minions(laura, max_depth=1)
        eq_(users, [peter])

        users = get_minions(laura, max_depth=99)
        eq_(users, [peter])

    def test_get_observed_users(self):
        gary = User.objects.create_user(
            'gary', 'gary@mozilla.com'
        )

        todd = User.objects.create_user(
            'todd', 'todd@mozilla.com',
        )
        profile = todd.get_profile()
        profile.manager = gary.email
        profile.save()

        mike = User.objects.create_user(
            'mike', 'mike@mozilla.com',
        )
        profile = mike.get_profile()
        profile.manager = todd.email
        profile.save()

        # peer to mike
        ben = User.objects.create_user(
            'ben', 'ben@mozilla.com',
        )
        profile = ben.get_profile()
        profile.manager = todd.email
        profile.save()

        laura = User.objects.create_user(
            'laura', 'laura@mozilla.com',
        )
        profile = laura.get_profile()
        profile.manager = mike.email
        profile.save()

        peter = User.objects.create_user(
            'peter', 'peter@mozilla.com',
        )
        profile = peter.get_profile()
        profile.manager = laura.email
        profile.save()

        # peer to peter
        lars = User.objects.create_user(
            'lars', 'lars@mozilla.com',
        )
        profile = lars.get_profile()
        profile.manager = laura.email
        profile.save()

        ## now we can start the actual testing
        # gary
        ieq_(
            get_observed_users(gary, depth=1, max_depth=2),
            [todd, mike, ben]
        )
        ieq_(
            get_observed_users(gary, depth=1, max_depth=1),
            [todd]
        )

        # todd
        ieq_(
            get_observed_users(todd, depth=1, max_depth=2),
            [mike, laura, ben, gary]
        )
        ieq_(
            get_observed_users(todd, depth=1, max_depth=1),
            [mike, ben, gary]
        )

        # mike
        ieq_(
            get_observed_users(mike, depth=1, max_depth=2),
            [laura, ben, peter, lars, todd]
        )
        ieq_(
            get_observed_users(mike, depth=1, max_depth=1),
            [laura, ben, todd]
        )

        # laura
        ieq_(
            get_observed_users(laura, depth=1, max_depth=2),
            [peter, lars, mike]
        )
        ieq_(
            get_observed_users(laura, depth=1, max_depth=1),
            [peter, lars, mike]
        )

        # peter
        ieq_(
            get_observed_users(peter, depth=1, max_depth=2),
            [lars, laura]
        )
        ieq_(
            get_observed_users(peter, depth=1, max_depth=1),
            [lars, laura]
        )

        # add followings
        FollowingUser.objects.create(
            follower=peter,
            following=gary
        )

        # peter, again
        ieq_(
            get_observed_users(peter, depth=1, max_depth=2),
            [lars, laura, gary]
        )
        ieq_(
            get_observed_users(peter, depth=1, max_depth=1),
            [lars, laura, gary]
        )

        # add blacklisting
        BlacklistedUser.objects.create(
            observer=peter,
            observable=lars,
        )

        # peter, again
        ieq_(
            get_observed_users(peter, depth=1, max_depth=2),
            [laura, gary]
        )
        ieq_(
            get_observed_users(peter, depth=1, max_depth=1),
            [laura, gary]
        )

    def test_get_observing_users(self):
        gary = User.objects.create_user(
            'gary', 'gary@mozilla.com'
        )

        todd = User.objects.create_user(
            'todd', 'todd@mozilla.com',
        )
        profile = todd.get_profile()
        profile.manager = gary.email
        profile.save()

        mike = User.objects.create_user(
            'mike', 'mike@mozilla.com',
        )
        profile = mike.get_profile()
        profile.manager = todd.email
        profile.save()

        # peer to mike
        ben = User.objects.create_user(
            'ben', 'ben@mozilla.com',
        )
        profile = ben.get_profile()
        profile.manager = todd.email
        profile.save()

        laura = User.objects.create_user(
            'laura', 'laura@mozilla.com',
        )
        profile = laura.get_profile()
        profile.manager = mike.email
        profile.save()

        peter = User.objects.create_user(
            'peter', 'peter@mozilla.com',
        )
        profile = peter.get_profile()
        profile.manager = laura.email
        profile.save()

        # peer to peter
        lars = User.objects.create_user(
            'lars', 'lars@mozilla.com',
        )
        profile = lars.get_profile()
        profile.manager = laura.email
        profile.save()

        ## now we can start the actual testing
        # gary
        ieq_(
            get_observing_users(gary, depth=1, max_depth=2),
            [todd]
        )
        ieq_(
            get_observing_users(gary, depth=1, max_depth=1),
            [todd]
        )

        # todd
        ieq_(
            get_observing_users(todd, depth=1, max_depth=2),
            [mike, ben, gary]
        )
        ieq_(
            get_observing_users(todd, depth=1, max_depth=1),
            [mike, ben, gary]
        )

        # laura
        ieq_(
            get_observing_users(laura, depth=1, max_depth=2),
            [peter, lars, mike, todd]
        )
        ieq_(
            get_observing_users(laura, depth=1, max_depth=1),
            [peter, lars, mike]
        )

        # peter
        ieq_(
            get_observing_users(peter, depth=1, max_depth=2),
            [lars, laura, mike]
        )
        ieq_(
            get_observing_users(peter, depth=1, max_depth=1),
            [lars, laura]
        )

        # add followings
        FollowingUser.objects.create(
            follower=gary,
            following=peter
        )

        # peter, again
        ieq_(
            get_observing_users(peter, depth=1, max_depth=2),
            [lars, laura, mike, gary]
        )
        ieq_(
            get_observing_users(peter, depth=1, max_depth=1),
            [lars, laura, gary]
        )

        # add blacklisting
        BlacklistedUser.objects.create(
            observer=lars,
            observable=peter,
        )

        # peter, again
        ieq_(
            get_observing_users(peter, depth=1, max_depth=2),
            [laura, mike, gary]
        )
        ieq_(
            get_observing_users(peter, depth=1, max_depth=1),
            [laura, gary]
        )

        # lars blacklists laura
        BlacklistedUser.objects.create(
            observer=lars,
            observable=laura,
        )

        # laura, again
        ieq_(
            get_observing_users(laura, depth=1, max_depth=2),
            [peter, mike, todd]
        )
        ieq_(
            get_observing_users(laura, depth=1, max_depth=1),
            [peter, mike]
        )

        # mike blacklists laura
        BlacklistedUser.objects.create(
            observer=mike,
            observable=laura,
        )

        # laura, again
        ieq_(
            get_observing_users(laura, depth=1, max_depth=2),
            [peter, todd]
        )
        ieq_(
            get_observing_users(laura, depth=1, max_depth=1),
            [peter]
        )
