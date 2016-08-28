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
    file.write("\n(%s) %s" % (group, group_id))


def subgroup(group, group_id, subgroup, subgroup_id, verbose):
    file.write("\n(%s/%s) %s / %s" % (group_id, subgroup_id, group, subgroup))


def task(group, subgroup, task, task_id, data, verbose):
    print("\n(%d) %s" % (task_id, task))

    description = data['description']
    print("\n%s" % description)

    notes = data['notes']
    if notes:
        print("  Notes:")
    for note in notes:
        print("  * %s" % note)

    props = data['properties']
    if props:
        print("  Properties:")
    for prop in props:
        print("  * %s" % prop)
