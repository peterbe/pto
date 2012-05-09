# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import re
import datetime


def get_weekday_dates(start, end):
    while start <= end:
        if start.weekday() < 5:
            yield start
        start += datetime.timedelta(days=1)


class DatetimeParseError(Exception):
    pass


def parse_datetime(datestr):
    _regex = re.compile('\d{13}|\d{10}\.\d{0,4}|\d{10}')
    _parsed = _regex.findall(datestr)
    if _parsed:
        datestr = _parsed[0]
        if len(datestr) >= len('1285041600000'):
            return datetime.datetime.fromtimestamp(float(datestr) / 1000)
        if len(datestr) >= len('1283140800'):
            return datetime.datetime.fromtimestamp(float(datestr))
    raise DatetimeParseError(datestr)
