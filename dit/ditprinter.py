# -*- coding: utf-8 -*-

from .data_utils import time_spent_on

file = None
statussing = False
listing = False
options = {}


def setup(_file, _options, _statussing, _listing):
    global file, options, statussing, listing
    file = _file
    options = _options
    listing = _listing
    statussing = _statussing


def begin():
    pass


def end():
    pass


def group(group, group_id):
    file.write("\n[%s] %s\n" % (group_id, group))


def subgroup(group, group_id, subgroup, subgroup_id):
    file.write("\n[%s/%s] %s\n" % (group_id, subgroup_id, subgroup))


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    # get options
    verbose = options.get('verbose', False)
    concluded = options.get('concluded', False)

    # get data
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
    file.write("\n[%s/%s/%s] %s" % (group_id, subgroup_id, task_id, task))

    if description:
        file.write("\n  %s" % description)

    if created_at:
        file.write('\n  * Created at: %s' % created_at)

    if verbose or statussing:
        if updated_at:
            file.write('\n  * Updated at: %s' % updated_at)

    if concluded:
        if concluded_at:
            file.write('\n  * Concluded at: %s' % concluded_at)

    if time_spent:
        file.write('\n  ~ Time spent: %s' % time_spent)

    if not statussing or (verbose and statussing):
        if notes:
            file.write("\n  Notes:")
        for note in notes:
            file.write("\n  * %s" % note)

        if props:
            file.write("\n  Properties:")
        for prop in props:
            file.write("\n  * %s: %s" % (prop['name'], prop['value']))

    if not statussing:
        if logbook:
            file.write("\n  Logbook:")

        i = 0 if verbose else -3
        for log in logbook[i:]:
            file.write("\n  + [%s]--[%s]" % (log['in'], log['out']))

    file.write("\n")
