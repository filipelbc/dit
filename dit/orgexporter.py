# -*- coding: utf-8 -*-

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
    file.write("\n* %s\n" % group)


def subgroup(group, group_id, subgroup, subgroup_id):
    file.write("\n** %s\n" % subgroup)


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    if data.get('concluded_at', None) and not options.get('concluded', False):
        return

    description = data.get('description', None)
    file.write("\n*** %s" % description)

    notes = data.get('notes', [])
    for note in notes:
        file.write("\n  + %s" % note)

    props = data.get('properties', [])
    if props:
        file.write("\n:PROPERTIES:")
    for prop in props:
        file.write("\n:%s: %s" % (prop['name'], prop['value']))
    if props:
        file.write("\n:END:")

    logbook = data.get('logbook', [])
    if logbook:
        file.write("\n:LOGBOOK:")
    for log in logbook:
        file.write("\nCLOCK: [%s]--[%s]" % (log['in'], log['out']))
    if logbook:
        file.write("\n:END:")

    file.write("\n")
