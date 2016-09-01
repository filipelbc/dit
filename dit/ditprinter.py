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
    file.write("\n(%s) %s\n" % (group_id, group))


def subgroup(group, group_id, subgroup, subgroup_id, verbose):
    file.write("\n(%s/%s) %s / %s\n" % (group_id, subgroup_id, group, subgroup))


def task(group, group_id, subgroup, subgroup_id, task, task_id, data, verbose):
    file.write("\n(%s/%s/%s) %s" % (group_id, subgroup_id, task_id, task))

    description = data['description']
    file.write("\n%s" % description)

    notes = data['notes']
    if notes:
        file.write("  Notes:")
    for note in notes:
        file.write("  * %s" % note['value'])

    props = data['properties']
    if props:
        file.write("  Properties:")
    for prop in props:
        file.write("  * %s: %s" % (prop['name'], prop['value']))

    file.write("\n")
