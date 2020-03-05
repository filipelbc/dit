# -*- coding: utf-8 -*-

import io
import sys
import subprocess
from datetime import timedelta

from .dit import names_to_string
from .utils import (
    apply_filters,
    convert_datetimes,
    dt2str,
    now,
)

_0_seconds = timedelta(0)

_file = None
_isatty = False
_pager = None
_days = {}
_options = {
    'filters': {}
}
_now = None


# ===========================================
# Colors


def _ca(string):
    if _isatty:
        return '\033[2;34m' + string + '\033[0m'
    return string


def _cc(string):
    if _isatty:
        return '\033[2;31m' + string + '\033[0m'
    return string


def _cd(string):
    if _isatty:
        return '\033[2;32m' + string + '\033[0m'
    return string


def _ce(string):
    if _isatty:
        return '\033[0;36m' + string + '\033[0m'
    return string


# ===========================================
# Write helpers


def _write(string=''):
    _file.write('%s\n' % string)


# ===========================================
# Logic helpers

def _lazy_now():
    global _now
    if _now is None:
        _now = now()
    return _now


def _calc_delta(log_entry):
    if log_entry[1] is None:
        return _lazy_now() - log_entry[0]
    return log_entry[1] - log_entry[0]


# ===========================================
# API


def setup(file, options):
    global _file
    global _options
    global _isatty
    _file = file
    _isatty = file.isatty()
    _options.update(options)


def begin():
    if _isatty:
        global _pager
        global _file
        _pager = subprocess.Popen(['less', '-F', '-R', '-S', '-X', '-K'],
                                  stdin=subprocess.PIPE, stdout=sys.stdout)
        _file = io.TextIOWrapper(_pager.stdin, 'UTF-8')


def end():
    for d, logs in sorted(_days.items(), reverse=True):
        total = sum(map(_calc_delta, logs), _0_seconds)

        _write('%s (%s)' % (_ca(d.strftime(r'%A %x')), _ce('%s' % total)))
        for lin, lout, name, title in sorted(logs, reverse=True):
            string = '  - %s' % dt2str(lin)
            lout_s = dt2str(lout) if lout else 'ongoing'
            string += ' ~ %s (%s)' % (lout_s, _ce('%s' % _calc_delta([lin, lout])))
            string += ' : [%s] %s' % (_cc(name), _cd(title))
            _write(string)

    if _isatty:
        _file.close()
        _pager.wait()


def group(group, group_id):
    pass


def subgroup(group, group_id, subgroup, subgroup_id):
    pass


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    filters = _options['filters']

    data = apply_filters(convert_datetimes(data), filters)
    if not data:
        return

    logbook = data.get('logbook', [])

    if not logbook:
        return

    for log in logbook:
        d = log['in'].date()

        if d not in _days:
            _days[d] = []

        _days[d].append((
            log['in'],
            log['out'],
            names_to_string(group, subgroup, task),
            data.get('title'),
        ))