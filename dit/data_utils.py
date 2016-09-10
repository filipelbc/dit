# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

# Auxiliary

_fmt = r'%Y-%m-%d %H:%M:%S'


def _timedelta_to_str(d):
    remainder = d.seconds + 3600 * d.days
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    s = ""
    if hours != 0:
        s += "%sh" % hours
    if minutes != 0 or hours != 0:
        s += "%sm" % minutes
    if seconds != 0 or minutes != 0 or hours != 0:
        s += "%ss" % seconds
    return s


def _to_timedelta(log):
    t_in = datetime.strptime(log['in'], _fmt)
    t_out = datetime.strptime(log['out'], _fmt)
    return t_out - t_in

# Main


def time_spent_on(logbook):
    d = timedelta(seconds=0)
    for logentry in logbook:
        if logentry['out']:
            d += _to_timedelta(logentry)
    return _timedelta_to_str(d)


def now():
    return datetime.now().strftime(_fmt)
