# -*- coding: utf-8 -*-

from .data_utils import time_spent_on

_file = None
_isatty = False
_options = {
    'verbose': False,
    'concluded': False,
    'statussing': False,
    'compact_header': False,
}


def _cg(string):
    if _isatty:
        return '\033[2;34m' + string + '\033[0m'
    return string


def _cs(string):
    if _isatty:
        return '\033[2;35m' + string + '\033[0m'
    return string


def _ct(string):
    if _isatty:
        return '\033[2;31m' + string + '\033[0m'
    return string


def _ci(string):
    if _isatty:
        return '\033[2;32m' + string + '\033[0m'
    return string


def _cp(string):
    if _isatty:
        return '\033[0;36m' + string + '\033[0m'
    return string


def _write(string=''):
    _file.write('%s\n' % string)


def _write_p(name, string=''):
    _write('  %s%s' % (_cp(name + ':'), (' ' + string) if string else ''))


def setup(file, options):
    global _file
    global _options
    global _isatty
    _file = file
    _isatty = file.isatty()
    _options.update(options)


def begin():
    pass


def end():
    pass


def group(group, group_id):
    if _options.get('compact_header'):
        return
    _write(_cg('[%s] %s' % (group_id, group)))


def subgroup(group, group_id, subgroup, subgroup_id):
    if _options.get('compact_header'):
        return
    _write(_cs('[%s/%s] %s' % (group_id, subgroup_id, subgroup)))


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    # options
    verbose = _options.get('verbose')
    concluded = _options.get('concluded')
    statussing = _options.get('statussing')

    # data
    concluded_at = data.get('concluded_at', None)

    if concluded_at and not concluded:
        return

    created_at = data.get('created_at', None)
    updated_at = data.get('updated_at', None)
    title = data.get('title', None)
    notes = data.get('notes', [])
    properties = data.get('properties', {})
    logbook = data.get('logbook', [])

    # write
    if _options.get('compact_header'):
        _write(_cg('[%s/%s/%s]' % (group_id, subgroup_id, task_id)) + ' ' +
               _ct('%s/%s/%s' % (group, subgroup, task)))
    else:
        _write(_ct('[%s/%s/%s] %s' % (group_id, subgroup_id, task_id, task)))

    if title:
        _write('  %s' % _ci(title))

    if properties and (verbose or not statussing):
        _write_p('Properties')
        for prop_name in sorted(properties.keys()):
            _write('  - %s: %s' % (prop_name, properties[prop_name]))

    if notes and (verbose or not statussing):
        _write_p('Notes')
        for note in notes:
            _write('  - %s' % note)

    if created_at and verbose and not statussing:
        _write_p('Created at', created_at)

    if updated_at and verbose and not statussing:
        _write_p('Updated at', updated_at)

    if concluded_at and verbose:
        _write_p('Concluded at', concluded_at)

    if logbook:
        if statussing and not verbose:
            log = logbook[-1]
            _write('  Spent %s; %s.' % (time_spent_on(logbook),
                                        ('clocked out at %s' % log['out'])
                                        if log['out'] else
                                        ('clocked in at %s' % log['in'])))
        else:
            _write_p('Total time spent', time_spent_on(logbook))
            if statussing:
                _write(_cp('  Last logbook entry:'))
                i = -1
            elif verbose:
                _write(_cp('  Logbook:'))
                i = 0
            else:
                _write(_cp('  Last logbook entries:'))
                i = -3

            for log in logbook[i:]:
                if log['out']:
                    _write('  - %s ~ %s' % (log['in'], log['out']))
                else:
                    _write('  - %s' % log['in'])
