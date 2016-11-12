# -*- coding: utf-8 -*-

_file = None
_options = {
    'concluded': False,
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
    write("* %s\n" % group)


def subgroup(group, group_id, subgroup, subgroup_id):
    write("** %s\n" % subgroup)


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    # options
    concluded = _options.get('concluded')

    # data
    concluded_at = data.get('concluded_at', None)

    if concluded_at and not concluded:
        return

    # write
    title = data.get('title', None)
    write("*** %s" % title)

    properties = data.get('properties', [])
    if properties:
        write(":PROPERTIES:")
    for prop_name in properties:
        write(":%s: %s" % (prop_name, properties[prop_name]))
    if properties:
        write(":END:")

    logbook = data.get('logbook', [])
    if logbook:
        write(":LOGBOOK:")
    for log in logbook:
        write("CLOCK: [%s]--[%s]" % (log['in'], log['out']))
    if logbook:
        write(":END:")

    notes = data.get('notes', [])
    for note in notes:
        write("- %s" % note)

    write()
