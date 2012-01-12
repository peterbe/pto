# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from test_utils import TestCase
from nose.tools import eq_, ok_


class TestUtils(TestCase):

    def test_get_weekday_dates(self):
        from dates.utils import get_weekday_dates
        d1 = datetime.date(2018, 1, 1)  # a Monday
        d2 = datetime.date(2018, 1, 9)  # next Tuesday
        dates = list(get_weekday_dates(d1, d2))
        eq_(dates[0].strftime('%A'), 'Monday')
        eq_(dates[1].strftime('%A'), 'Tuesday')
        eq_(dates[2].strftime('%A'), 'Wednesday')
        eq_(dates[3].strftime('%A'), 'Thursday')
        eq_(dates[4].strftime('%A'), 'Friday')
        eq_(dates[5].strftime('%A'), 'Monday')
        eq_(dates[6].strftime('%A'), 'Tuesday')

    def test_parse_datetime(self):
        from dates.utils import parse_datetime, DatetimeParseError
        eq_(parse_datetime('1285041600000').year, 2010)
        eq_(parse_datetime('1283140800').year, 2010)
        eq_(parse_datetime('1286744467.0').year, 2010)
        self.assertRaises(DatetimeParseError, parse_datetime, 'junk')
