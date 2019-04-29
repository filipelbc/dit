# -*- coding: utf-8 -*-

import io
import sys
import subprocess
from datetime import timedelta

from .dit import names_to_string
from .utils import (dt2str, td2str,
                    time_spent_on,
                    convert_datetimes,
                    apply_filters)

_file = None
_isatty = False
_pager = None
_options = {
    'verbose': False,
    'id-only': False,
    'name-only': False,
    'concluded': False,
    'statussing': False,
    'compact-header': False,
    'sum': False,
    'filters': {}
}
_overall_time_spent = timedelta()

_group_string = None
_subgroup_string = None

# ===========================================
# Colors


def _ca(string):
    if _isatty:
        return '\033[2;34m' + string + '\033[0m'
    return string


def _cb(string):
    if _isatty:
        return '\033[2;35m' + string + '\033[0m'
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


def _cf(string):
    if _isatty:
        return '\033[0;34m' + string + '\033[0m'
    return string

# ===========================================
# Write helpers


def _write(string=''):
    _file.write('%s\n' % string)


def _write_p(name, string=''):
    _write('  %s%s' % (_ce(name + ':'), (' ' + string) if string else ''))

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
    if _options['sum']:
        _write('\n%s %s' % (_cf("Overall time spent:"),
                            td2str(_overall_time_spent)))
    if _isatty:
        _file.close()
        _pager.wait()


def group(group, group_id):
    if not _options.get('compact-header'):
        global _group_string
        _group_string = _ca('[%s] %s' % (group_id, group))


def subgroup(group, group_id, subgroup, subgroup_id):
    if not _options.get('compact-header'):
        global _subgroup_string
        _subgroup_string = _cb('[%s/%s] %s' % (group_id, subgroup_id, subgroup))


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    # options
    verbose = _options['verbose']
    id_only = _options['id-only']
    name_only = _options['name-only']
    concluded = _options['concluded']
    statussing = _options['statussing']
    filters = _options['filters']

    if data.get('concluded_at') and not concluded:
        return

    # data preprocessor
    data = apply_filters(convert_datetimes(data), filters)
    if not data:
        return

    # write
    if id_only:
        _write('%s/%s/%s' % (group_id, subgroup_id, task_id))
        return
    elif name_only:
        _write(names_to_string(group, subgroup, task))
        return

    if _options.get('compact-header'):
        _write(_ca('[%s/%s/%s]' % (group_id, subgroup_id, task_id)) + ' ' +
               _cc(names_to_string(group, subgroup, task)))
    else:
        global _group_string, _subgroup_string
        if _group_string:
            _write(_group_string)
            _group_string = None
        if _subgroup_string:
            _write(_subgroup_string)
            _subgroup_string = None
        _write(_cc('[%s/%s/%s] %s' % (group_id, subgroup_id, task_id, task)))

    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    concluded_at = data.get('concluded_at')
    title = data.get('title')
    notes = data.get('notes', [])
    properties = data.get('properties', {})
    logbook = data.get('logbook', [])

    if title:
        _write('  %s' % _cd(title))

    if properties and (verbose or not statussing):
        _write_p('Properties')
        for prop_name in sorted(properties.keys()):
            _write('  - %s: %s' % (prop_name, properties[prop_name]))

    if notes and (verbose or not statussing):
        _write_p('Notes')
        for note in notes:
            _write('  - %s' % note)

    if created_at and verbose and not statussing:
        _write_p('Created at', dt2str(created_at))

    if updated_at and verbose and not statussing:
        _write_p('Updated at', dt2str(updated_at))

    if concluded_at and verbose:
        _write_p('Concluded at', dt2str(concluded_at))

    if logbook:
        global _overall_time_spent
        time_spent = time_spent_on(logbook)
        _overall_time_spent += time_spent

        if statussing and not verbose:
            log = logbook[-1]
            string = '  '

            def _phrase(description, value):
                return _ce(description) + ' ' + value + '. '

            if time_spent:
                string += "%s %s. " % (_ce('Spent'), td2str(time_spent))
            if log['out']:
                string += "%s %s." % (_ce('Clocked out at'), dt2str(log['out']))
            else:
                string += "%s %s." % (_cf('Clocked in at'), dt2str(log['in']))
            _write(string)

        else:
            _write_p('Time spent', td2str(time_spent))
            if statussing:
                _write(_ce('  Last logbook entry:'))
                i = -1
            elif verbose:
                _write(_ce('  Logbook:'))
                i = 0
            else:
                _write(_ce('  Last logbook entries:'))
                i = -3

            for log in logbook[i:]:
                string = '  - %s' % dt2str(log['in'])
                if log['out']:
                    string += ' ~ %s (%s)' % (dt2str(log['out']), td2str(log['out'] - log['in']))
                _write(string)
