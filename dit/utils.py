# -*- coding: utf-8 -*-

import re
import os
from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone

from .exceptions import ArgumentException

# Auxiliary

DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S %z'


def td2str(td):
    remainder = td.seconds + 3600 * td.days
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    s = ""
    if hours != 0:
        s += "%sh" % hours
    if minutes != 0:
        s += "%s%smin" % (' ' if s else '', minutes)
    if seconds != 0:
        s += "%s%ss" % (' ' if s else '', seconds)
    return s


def dt2str(dt):
    return dt.strftime(DATETIME_FORMAT)


def str2dt(string):
    return datetime.strptime(string, DATETIME_FORMAT)

# The function `now` needs to be mocked when running tests
# In order to have progressing time, we maintain a file with an incrementing
# integer
if os.path.isfile('DIT_TESTING'):

    LOCALZONE = timezone(timedelta(-1, 79200), 'BRST')
    TODAY = datetime(2016, 9, 10, 0, 0, 0, 0, LOCALZONE)

    _base_now = datetime(2016, 9, 10, 18, 50, 43, 0, LOCALZONE)

    def now():
        with open('DIT_TESTING', 'r') as f:
            i = int(f.read())
        now = _base_now + timedelta(seconds=(i * 40))
        with open('DIT_TESTING', 'w') as f:
            f.write(str(i + 1))
        return dt2str(now)

else:

    LOCALZONE = get_localzone()
    TODAY = datetime.now(LOCALZONE).replace(hour=0,
                                            minute=0,
                                            second=0,
                                            microsecond=0)

    def now():
        return dt2str(datetime.now(LOCALZONE))


def time_spent_on(logbook):
    time_spent = timedelta()
    for log in logbook:
        if log['out']:
            time_spent += log['out'] - log['in']
    return time_spent


def convert_datetimes(data):
    for key in ['created_at', 'updated_at', 'concluded_at']:
        if key in data:
            data[key] = str2dt(data[key])
    logbook = data.get('logbook', [])
    for log in logbook:
        log['in'] = str2dt(log['in'])
        log['out'] = str2dt(log['out']) if log['out'] else None
    return data

# ===========================================
# Filtering


def _interpret_date(string):

    days_p = r'(?P<days>[+-]?\d+) ?d(ays?)?'
    hours_p = r'(?P<hours>[+-]?\d+) ?h(ours?)?'
    minutes_p = r'(?P<minutes>[+-]?\d+) ?min(utes?)?'

    days_m = re.search(days_p, string)
    hours_m = re.search(hours_p, string)
    minutes_m = re.search(minutes_p, string)

    if days_m or hours_m or minutes_m:
        dt = TODAY
        if days_m:
            days = days_m.group('days')
            dt += timedelta(days=int(days))
        if hours_m:
            hours = hours_m.group('hours')
            dt += timedelta(hours=int(hours))
        if minutes_m:
            minutes = minutes_m.group('minutes')
            dt += timedelta(minutes=int(minutes))
        return dt

    raise ArgumentException('Unrecognized date/time string: %s' % string)


def apply_filter_where(data, where):
    name = where[0]
    value = where[1]

    properties = data.get('properties', {})

    if name in properties and re.search(value, properties[name]):
        return data
    return {}


def apply_filter_to(data, to):
    if 'created_at' in data and to <= data['created_at']:
        return {}
    logbook = data.get('logbook', [])

    i = 0
    while i > - len(logbook):
        if logbook[i - 1]['in'] <= to:
            break
        else:
            i -= 1
    if i != 0:
        logbook = logbook[:i]

    data['logbook'] = logbook
    return data


def apply_filter_from(data, fron):
    if 'concluded_at' in data and fron >= data['concluded_at']:
        return {}
    logbook = data.get('logbook', [])

    i = 0
    while i < len(logbook):
        if logbook[i]['in'] >= fron:
            break
        else:
            i += 1
    if i != 0:
        logbook = logbook[i:]

    data['logbook'] = logbook
    return data


def init_filters(filters):
    for key in filters:
        if key in ['from', 'to']:
            filters[key] = _interpret_date(filters[key])
        elif key == 'where':
            filters[key][1] = re.compile(filters[key][1])


def apply_filters(data, filters):

    if data and 'where' in filters:
        data = apply_filter_where(data, filters['where'])

    if data and 'from' in filters:
        data = apply_filter_from(data, filters['from'])

    if data and 'to' in filters:
        data = apply_filter_to(data, filters['to'])

    return data
