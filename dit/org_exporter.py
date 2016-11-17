# -*- coding: utf-8 -*-

from datetime import datetime

from .dit import State, state
from .utils import DATETIME_FORMAT

_file = None
_options = {
    'concluded': False,
}


def _(string):
    return datetime.strptime(string, DATETIME_FORMAT).strftime(r'%Y-%m-%d %a %H:%M')


def _get_state(data):
    s = state(data)
    if s == State.TODO:
        return "TODO "
    elif s == State.CONCLUDED:
        return "DONE "
    else:
        return ""


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
    _write("* %s" % group)
    _write()


def subgroup(group, group_id, subgroup, subgroup_id):
    _write("** %s" % subgroup)
    _write()


def task(group, group_id, subgroup, subgroup_id, task, task_id, data):
    # options
    concluded = _options['concluded']

    # data
    concluded_at = data.get('concluded_at')
    if concluded_at and not concluded:
        return

    # write
    title = data.get('title', None)
    _write("*** %s%s" % (_get_state(data), title))

    properties = data.get('properties', [])
    if properties:
        _write(":PROPERTIES:")
    for prop_name in sorted(properties.keys()):
        _write(":%s: %s" % (prop_name, properties[prop_name]))
    if properties:
        _write(":END:")

    if concluded_at:
        _write("CLOSED: [%s]" % _(concluded_at))

    logbook = data.get('logbook', [])
    if logbook:
        _write(":LOGBOOK:")
    for log in logbook:
        if log['out']:
            _write("CLOCK: [%s]--[%s]" % (_(log['in']), _(log['out'])))
        else:
            _write("CLOCK: [%s]" % _(log['in']))
    if logbook:
        _write(":END:")

    notes = data.get('notes', [])
    for note in notes:
        _write("- %s" % note)

    _write()
