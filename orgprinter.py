# -*- coding: utf-8 -*-
#
# Python file
#
# Author:        Filipe L B Correia <filipelbc@gmail.com>
#
# About:         Dit printer plugin
#
# =============================================================================

file = None


def group(group, group_id):
    file.write("\n* %s\n" % group)


def subgroup(group, group_id, subgroup, subgroup_id, verbose):
    file.write("\n** %s\n" % subgroup)


def task(group, subgroup, task, task_id, data, verbose):
    description = data['description']
    file.write("\n*** %s" % description)

    notes = data['notes']
    for note in notes:
        file.write("\n  - %s" % note['value'])

    props = data['properties']
    if props:
        file.write("\n:PROPERTIES:")
    for prop in props:
        file.write("\n:%s: %s" % (prop['name'], prop['value']))
    if props:
        file.write("\n:END:")

    logbook = data['logbook']
    if logbook:
        file.write("\n:LOGBOOK:")
    for log in logbook:
        file.write("\nCLOCK: [%s]--[%s]" % (log['in'], log['out']))
    if logbook:
        file.write("\n:END:")

    file.write("\n")
