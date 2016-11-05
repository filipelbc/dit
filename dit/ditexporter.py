# -*- coding: utf-8 -*-

from .data_utils import time_spent_on

_file = None
_options = {
    'verbose': False,
    'concluded': False,
    'statussing': False,
}


def write(string=''):
    _file.write('\n%s' % string)


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
    write('[%s] %s\n' % (group_id, group))


def subgroup(group, group_id, subgroup, subgroup_id):
    write('[%s/%s] %s\n' % (group_id, subgroup_id, subgroup))


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
    description = data.get('description', None)
    notes = data.get('notes', [])
    props = data.get('properties', [])
    logbook = data.get('logbook', [])

    if logbook:
        time_spent = time_spent_on(logbook)
    else:
        time_spent = None

    # write
    write('[%s/%s/%s] %s' % (group_id, subgroup_id, task_id, task))

    if description:
        write('  %s' % description)

    if created_at and not statussing:
        write('  * Created at: %s' % created_at)

    if verbose or statussing:
        if updated_at:
            write('  * Updated at: %s' % updated_at)

    if concluded:
        if concluded_at:
            write('  * Concluded at: %s' % concluded_at)

    if time_spent:
        write('  ~ Time spent: %s' % time_spent)

    if not statussing or (verbose and statussing):
        if notes:
            write('  Notes:')
        for note in notes:
            write('  * %s' % note)

        if props:
            write('  Properties:')
        for prop in props:
            write('  * %s: %s' % (prop['name'], prop['value']))

    if not statussing:
        if logbook:
            write('  Logbook:')

        i = 0 if verbose else -3
        for log in logbook[i:]:
            write('  + [%s]--[%s]' % (log['in'], log['out']))
    else:
        if logbook:
            log = logbook[-1]
            write('  [%s]--[%s]' % (log['in'], log['out']))

    write()
