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
from django.test import TestCase
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

    def test_get_hours_left(self):
        from dates.utils.pto_left import get_hours_left
        print "!TEST CURRENTLY INCOMPLETE test_get_hours_left()"
