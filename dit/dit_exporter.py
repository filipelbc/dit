# -*- coding: utf-8 -*-

from .data_utils import time_spent_on

_file = None
_options = {
    'verbose': False,
    'concluded': False,
    'statussing': False,
}


def _write(string=''):
    _file.write('%s\n' % string)


def setup(file, options):
    global _file
    global _options
    _file = file
    _options.update(options)


def begin():
    pass


def end():
    pass


def group(group, group_id):
    _write('[%s] %s' % (group_id, group))


def subgroup(group, group_id, subgroup, subgroup_id):
    _write('[%s/%s] %s' % (group_id, subgroup_id, subgroup))


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

    if logbook:
        time_spent = time_spent_on(logbook)
    else:
        time_spent = None

    # write
    _write('[%s/%s/%s] %s' % (group_id, subgroup_id, task_id, task))

    if title:
        _write('  %s' % title)

    if created_at and verbose and not statussing:
        _write('  - Created at: %s' % created_at)

    if updated_at and verbose:
        _write('  - Updated at: %s' % updated_at)

    if concluded_at and verbose:
        _write('  - Concluded at: %s' % concluded_at)

    if time_spent:
        _write('  - Time spent: %s' % time_spent)

    if notes and (verbose or not statussing):
        _write('  Notes:')
        for note in notes:
            _write('  - %s' % note)

    if properties and (verbose or not statussing):
        _write('  Properties:')
        for prop_name in sorted(properties.keys()):
            _write('  - %s: %s' % (prop_name, properties[prop_name]))

    if logbook:
        if not statussing:
            _write('  Logbook:')

        if statussing:
            i = -1
        elif verbose:
            i = 0
        else:
            i = -3

        prefix = '' if statussing else '- '

        for log in logbook[i:]:
            _write('  %s[%s]--[%s]' % (prefix, log['in'], log['out']))
