# -*- coding: utf-8 -*-

import io
import sys
import subprocess
from datetime import timedelta

from .dit import names_to_string
from .utils import (dt2str, td2str,
                    convert_datetimes,
                    apply_filters)

_0_seconds = timedelta(0)

_file = None
_isatty = False
_pager = None
_days = {}
_options = {
    'filters': {}
}


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
        total = sum(map(lambda x: x[1] - x[0], logs), _0_seconds)

        _write('%s (%s)' % (_ca(d.strftime(r'%A %x')), _ce('%s' % total)))
        for lin, lout, name, title in sorted(logs, reverse=True):
            string = '  - %s' % dt2str(lin)
            if lout:
                string += ' ~ %s (%s)' % (dt2str(lout), _ce('%s' % (lout - lin)))
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
