# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone

# Auxiliary

DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S %z'


def _timedelta_to_str(d):
    remainder = d.seconds + 3600 * d.days
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    s = ""
    if hours != 0:
        s += "%sh" % hours
    if minutes != 0:
        s += "%sm" % minutes
    if seconds != 0:
        s += "%ss" % seconds
    return s


def _to_timedelta(log):
    t_in = datetime.strptime(log['in'], DATETIME_FORMAT)
    t_out = datetime.strptime(log['out'], DATETIME_FORMAT)
    return t_out - t_in

# Main Utilities


def time_spent_on(logbook):
    d = timedelta(seconds=0)
    for logentry in logbook:
        if logentry['out']:
            d += _to_timedelta(logentry)
    return _timedelta_to_str(d)

# The function `now` needs to be mocked when running tests
# In order to have progressing time, we maintain a file with an incrementing
# integer
if os.path.isfile('DIT_TESTING'):

    BASE_NOW = datetime(2016, 9, 10, 18, 57, 49, 0,
                        timezone(timedelta(-1, 79200), 'BRST'))

    def now():
        with open('DIT_TESTING', 'r') as f:
            i = int(f.read())
        now = BASE_NOW + timedelta(seconds=(i * 10))
        with open('DIT_TESTING', 'w') as f:
            f.write(str(i + 1))
        return now.strftime(DATETIME_FORMAT)

else:

    LOCALZONE = get_localzone()

    def now():
        return datetime.now(LOCALZONE).strftime(DATETIME_FORMAT)
