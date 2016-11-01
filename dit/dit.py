#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage: dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. If not specified, the
    closest ".dit" directory in the tree is used. If not found, '~/.dit' is
    used.

  --verbose, -v
    Prints detailed information of what is being done.

  --help, -h
    Prints this message and quits.

  Workflow <command>'s:

    new <name> [-: "description"]
      Creates a new task. You will be prompted for the "description" if it is
      not provided.

    workon <id> | <name> | --new, -n <name> [-: "description"]
      Starts clocking the specified task. If CURRENT is not halted, nothing is
      done. Sets CURRENT task.
      --new, -n
        Same as 'new' followed by 'workon'.

    halt [<id> | <name>]
      Stops clocking the CURRENT task or the specified one. Sets CURRENT to
      halted.

    append [<id> | <name>]
      If CURRENT is halted, undoes the 'halt'.

    cancel [<id> | <name>]
      Undoes the previous 'workon'.

    resume
      Same as 'workon CURRENT'.

    switchto <id> | <name> | --new, -n <name> [-: "description"]
      Same as 'halt' followed by 'workon T'.

    switchback
      Same as 'switchto T', where T is the last halted task that is not
      CURRENT.

    conclude [<id> | <name>]
      Concludes the CURRENT task or the selected one. Implies a 'halt'.

  Printing <command>'s:

    export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"]
           [<gid> | <gname>]
      Prints most information of the CURRENT subgroup or the selected one.
      --concluded, -a
        Include concluded tasks.
      --all, -a
        Select all groups and subgroups.
      --verbose, -v
        All information is exported.
      --output, -o
        File to which to write. Defaults to "stdout". Format is deduced from
        file extension if present.

    list
      This is a convenience alias for 'export', with "--output stdout".

    status [<gid> | <gname>]
      Prints an overview of the data for the CURRENT task or subgroup, or
      for the selected one.

  Task editing <command>'s:

    note [<name> | <id>] [-: "text"]
      Adds a note to the CURRENT task or the specified one.

    set [<name> | <id>] [-: "name" ["value"]]
      Sets a property for the CURRENT task or the specified one.

    edit [<name> | <id>]
      Opens the specified task for manual editing. Uses CURRENT task if none is
      specified. If $EDITOR environment variable is not set it does nothing.

  Other <command>'s:

    rebuild-index
      Rebuild the INDEX file. For use in case of manual modification of the
      contents of "--directory".

  "-:"
    Arguments preceeded by "-:" are necessary. If omited, then: a) if the
    $EDITOR environment variable is set, a text file will be open for
    editing the argument; b) otherwise, a simple prompt will be used.

  <name>: [["group-name"/]"subgroup-name"/]"task-name" | CURRENT

  <gname>: "group-name"[/"subgroup-name"[/"task-name"]] | CURRENT

  Note that a "-name" must begin with a letter to be valid. Group- and
  subgroup-names can be empty or a dot, which means no group and/or subgroup.

  Also note that CURRENT is not a valid argument for the command 'new'.

  <id>: [["group-id"/]"subgroup-id"/]"task-id"

  <gid>: "group-id"[/"subgroup-id"[/"task-id"]]
"""

import json
import os
import re
import subprocess
import sys

from enum import Enum
from getpass import getuser
from importlib import import_module
from tempfile import gettempdir

from .data_utils import now

# ===========================================
# Custom Exceptions


class DitException(Exception):
    pass


class ArgumentException(DitException):
    pass


class NoTaskSpecifiedCondition(DitException):
    pass

# ===========================================
# Constants


CURRENT_FN = "CURRENT"
PREVIOUS_FN = "PREVIOUS"
INDEX_FN = "INDEX"

PROHIBITED_FNS = [CURRENT_FN, PREVIOUS_FN, INDEX_FN]

SEPARATOR_CHAR = "/"
COMMENT_CHAR = "#"
NONE_CHAR = "_"
ROOT_NAME_CHAR = "."
ROOT_NAME = ""

DEFAULT_BASE_DIR = ".dit"
DEFAULT_BASE_PATH = "~/" + DEFAULT_BASE_DIR

# ===========================================
# Enumerators


class State(Enum):
    TODO = 1
    DOING = 2
    HALTED = 3
    CONCLUDED = 4

# ===========================================
# General Options


VERBOSE = False

# ===========================================
# Message output


def msg_normal(message):
    sys.stdout.write("%s\n" % message)


def msg_verbose(message):
    if VERBOSE:
        msg_normal(message)


def msg_warning(message):
    if VERBOSE:
        msg_normal(message)


def msg_error(message):
    sys.stdout.flush()
    sys.stderr.write("ERROR: %s\n" % message)


def msg_selected(group, subgroup, task):
    msg_verbose("Selected: %s" % _(group, subgroup, task))


def msg_usage():
    msg_normal(__doc__)

# ===========================================
# Command decorator


COMMAND_INFO = {}

SELECT_BY_NAME = "N"
SELECT_BY_GNAME = "G"


def command(letter, options, select):
    def wrapper(cmd):
        global COMMAND_INFO
        name = cmd.__name__.replace("_", "-")
        if name in COMMAND_INFO:
            raise Exception("Method '%s' is already registered as command.")
        COMMAND_INFO[name] = {'name': cmd.__name__,
                              'letter': letter,
                              'options': options,
                              'select': select}
        if letter and letter in COMMAND_INFO:
            raise Exception("Letter '%s' is already registered as command.")
        if letter:
            COMMAND_INFO[letter] = COMMAND_INFO[cmd.__name__]
        return cmd
    return wrapper

# ===========================================
# Path Discovery


def discover_base_path(directory):

    def bottomup_search(current_level, basename):
        path = os.path.join(current_level, basename)
        while not os.path.isdir(path):
            parent_level = os.path.dirname(current_level)
            if parent_level == current_level:
                return None
            current_level = parent_level
            path = os.path.join(current_level, basename)
        return path

    directory = directory\
        or bottomup_search(os.getcwd(), DEFAULT_BASE_DIR)\
        or DEFAULT_BASE_PATH

    return os.path.expanduser(directory)

# ===========================================
# To Nice String


def path_to_string(path):
    if path == os.path.expanduser(DEFAULT_BASE_PATH):
        return DEFAULT_BASE_PATH
    return os.path.relpath(path)


def task_name_to_string(name):
    if name is None:
        return NONE_CHAR
    elif name == ROOT_NAME:
        return ROOT_NAME_CHAR
    return name


def _(name, *more_names):
    s = task_name_to_string(name)
    for name in more_names:
        s += SEPARATOR_CHAR + task_name_to_string(name)
    return s

# ===========================================
# I/O


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        msg_verbose("Created: %s" % path_to_string(path))


def load_json_file(fp):
    if os.path.isfile(fp):
        with open(fp, 'r') as f:
            return json.load(f)
    return None


def save_json_file(fp, data):
    with open(fp, 'w') as f:
        f.write(json.dumps(data))


def make_tmp_fp(name, extension):
    name = re.sub(r'[^_A-Za-z0-9]', '_', name).strip('_') + '.' + extension

    path = os.path.join(gettempdir(), getuser(), "dit")
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.join(path, name)


def prompt(header, initial=None, extension='txt'):
    editor = os.environ.get('EDITOR', None)
    if editor:
        input_fp = make_tmp_fp(header, extension)
        with open(input_fp, 'w') as f:
            f.write(COMMENT_CHAR + ' ' + header + '\n')
            if initial:
                f.write(initial)
        subprocess.run([editor, input_fp])
        with open(input_fp, 'r') as f:
            lines = [line for line in f.readlines()
                     if not line.startswith(COMMENT_CHAR)]
        return (''.join(lines)).strip()

    elif not initial:
        return input(header + ': ').strip()

    else:
        raise DitException("$EDITOR environment variable is not set.")

# ===========================================
# Task Verification


def is_valid_task_name(name):
    return len(name) > 0 and name[0].isalpha() and name not in PROHIBITED_FNS


def is_valid_group_name(name):
    return name == ROOT_NAME or is_valid_task_name(name)


def is_valid_task_data(data):
    return isinstance(data, dict)

# ===========================================
# Task Data Manipulation


def state(task_data):
    if task_data.get('concluded_at', None):
        return State.CONCLUDED
    logbook = task_data.get('logbook', None)
    if len(logbook) > 0:
        last = logbook[-1]
        if last['out']:
            return State.HALTED
        else:
            return State.DOING
    else:
        return State.TODO


def data_clock_in(data):
    logbook = data.get('logbook', [])
    if len(logbook) > 0:
        last = logbook[-1]
        if not last['out']:
            msg_normal("Already clocked in.")
            return
    data.pop('concluded_at', None)
    data['logbook'] = logbook + [{'in': now(), 'out': None}]


def data_clock_append(data):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg_normal("Task has no clocking.")
        return
    last = logbook[-1]
    if not last['out']:
        msg_normal("Already clocked in.")
        return
    last['out'] = None


def data_clock_out(data):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg_normal("Already clocked out.")
        return
    last = logbook[-1]
    if last['out']:
        msg_normal("Already clocked out.")
        return
    last['out'] = now()
    data['logbook'] = logbook


def data_clock_cancel(data):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg_normal("Was not clocked in.")
        return
    last = logbook[-1]
    if last['out']:
        msg_normal("Was not clocked in.")
        return
    logbook.pop(-1)
    data['logbook'] = logbook


def data_conclude(data):
    if data.get('concluded_at', None):
        msg_normal("Already concluded.")
        return
    data['concluded_at'] = now()


def data_new(description=None):
    return {
        "description": description,
        "logbook": [],
        "properties": [],
        "notes": [],
        "created_at": now()
    }


def data_add_note(data, note_text):
    if 'notes' not in data:
        data['notes'] = []
    data['notes'].append(note_text)


def data_set_property(data, prop_name, prop_value):
    if 'properties' not in data:
        data['properties'] = []

    properties = data['properties']
    for prop in properties:
        if prop_name == prop['name']:
            prop['value'] = prop_value
            return
    properties.append({'name': prop_name, 'value': prop_value})

# ===========================================
# Dit Class


class Dit:

    current_group = None
    current_subgroup = None
    current_task = None
    current_halted = True

    previous_stack = []

    index = [[ROOT_NAME, [[ROOT_NAME, []]]]]

    base_path = None
    printer = None

    # ===========================================
    # Paths and files names

    def _setup_base_path(self, directory):
        path = discover_base_path(directory)
        make_dirs(path)
        msg_verbose("Using directory: %s" % path_to_string(path))
        self.base_path = path

    def _current_path(self):
        return os.path.join(self.base_path, CURRENT_FN)

    def _previous_path(self):
        return os.path.join(self.base_path, PREVIOUS_FN)

    def _index_path(self):
        return os.path.join(self.base_path, INDEX_FN)

    def _get_task_path(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup, task)
        if not os.path.isfile(path):
            raise DitException("No such task file: %s" % path)
        return path

    def _make_task_path(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup)
        make_dirs(path)
        return os.path.join(path, task)

    # ===========================================
    # Checks

    def _is_current(self, group, subgroup, task):
        return (task == self.current_task and
                subgroup == self.current_subgroup and
                group == self.current_group)

    # ===========================================
    # Task management

    def _create_task(self, group, subgroup, task, description):
        task_fp = self._make_task_path(group, subgroup, task)
        if os.path.isfile(task_fp):
            raise DitException("Task file already exists: %s" % task_fp)
        data = data_new(description)
        save_json_file(task_fp, data)
        self._add_to_index(group, subgroup, task)
        self._save_index()

    def _load_task_data(self, group, subgroup, task):
        task_fp = self._get_task_path(group, subgroup, task)
        data = load_json_file(task_fp)
        if not is_valid_task_data(data):
            raise DitException(
                "Task file contains invalid data: %s" % task_fp)
        return data

    def _save_task(self, group, subgroup, task, data):
        task_fp = self._make_task_path(group, subgroup, task)
        data['updated_at'] = now()
        save_json_file(task_fp, data)
        msg_verbose("Task saved: %s" % _(group, subgroup, task))

    # Current Task

    def _get_current(self):
        return (self.current_group,
                self.current_subgroup,
                None if self.current_halted else self.current_task)

    def _clear_current(self):
        self._set_current(None, None, None)

    def _set_current(self, group, subgroup, task, halted=False):
        self.current_group = group
        self.current_subgroup = subgroup
        self.current_task = task
        self.current_halted = halted

    def _save_current(self):
        current_data = {
            'group': self.current_group,
            'subgroup': self.current_subgroup,
            'task': self.current_task,
            'halted': self.current_halted
        }
        save_json_file(self._current_path(), current_data)
        msg_verbose("%s saved: %s%s" %
                    (CURRENT_FN, _(self.current_group,
                                   self.current_subgroup,
                                   self.current_task),
                     " (halted)" if self.current_halted else ""))

    def _load_current(self):
        current = load_json_file(self._current_path())
        if current is not None:
            self._set_current(current['group'],
                              current['subgroup'],
                              current['task'],
                              current['halted'])

    # Previous Task

    def _previous_add(self, group, subgroup, task):
        s = "%s/%s/%s" % (group, subgroup, task,)
        self.previous_stack.append(s)

    def _previous_remove(self, group, subgroup, task):
        s = "%s/%s/%s" % (group, subgroup, task,)
        self.previous_stack = [i for i in self.previous_stack if i != s]

    def _previous_pop(self):
        e = self.previous_stack.pop()
        return e.split("/")

    def _previous_empty(self):
        return len(self.previous_stack) == 0

    def _save_previous(self):
        save_json_file(self._previous_path(), self.previous_stack)
        msg_verbose("%s saved with %d tasks." % (
            PREVIOUS_FN, len(self.previous_stack),))

    def _load_previous(self):
        previous = load_json_file(self._previous_path())
        if previous is not None:
            self.previous_stack = previous

    # ===========================================
    # Index

    def _add_to_index(self, group, subgroup, task):
        group_id = -1
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                group_id = i
                break
        if group_id == -1:
            group_id = len(self.index)
            self.index.append([group, [[ROOT_NAME, []]]])

        subgroup_id = -1
        for i in range(len(self.index[group_id][1])):
            if self.index[group_id][1][i][0] == subgroup:
                subgroup_id = i
                break
        if subgroup_id == -1:
            subgroup_id = len(self.index[group_id][1])
            self.index[group_id][1].append([subgroup, []])

        self.index[group_id][1][subgroup_id][1].append(task)

    def _save_index(self):
        save_json_file(self._index_path(), self.index)
        msg_verbose("%s saved." % INDEX_FN)

    def _load_index(self):
        index_fp = self._index_path()
        index = load_json_file(index_fp)
        if index is not None:
            self.index = index

    def _rebuild_index(self):
        self.index = [[ROOT_NAME, [[ROOT_NAME, []]]]]
        c_group = ROOT_NAME
        c_subgroup = ROOT_NAME
        for root, dirs, files in os.walk(self.base_path):
            dirs.sort()
            for f in sorted(files):
                if not is_valid_task_name(f):
                    continue
                p = root[len(self.base_path) + 1:].split(os.sep)

                p = [i for i in p if i]
                if len(p) == 0:
                    group, subgroup = ROOT_NAME, ROOT_NAME
                elif len(p) == 1:
                    group, subgroup = p[0], ROOT_NAME
                elif len(p) == 2:
                    group, subgroup = p
                else:
                    continue

                if group != c_group:
                    c_group = group
                    c_subgroup = ROOT_NAME
                    self.index.append([group, [[ROOT_NAME, []]]])

                if subgroup != c_subgroup:
                    c_subgroup = subgroup
                    self.index[-1][1].append([subgroup, []])

                self.index[-1][1][-1][1].append(f)

        msg_verbose("%s rebuilt." % INDEX_FN)

    # ===========================================
    # Export

    # these are for internal use

    def _export_t_k(self, g, i, s, j, t, k, force_header=False):
        if force_header:
            if i > 0:
                self.printer.group(g[0], i)
            if j > 0:
                self.printer.subgroup(g[0], i, s[0], j)

        data = self._load_task_data(g[0], s[0], t)
        self.printer.task(g[0], i, s[0], j, t, k, data)

    def _export_s_j(self, g, i, s, j, force_header=False):
        if force_header and i > 0:
            self.printer.group(g[0], i)

        if j > 0:
            self.printer.subgroup(g[0], i, s[0], j)
        for k, t in enumerate(s[1]):
            self._export_t_k(g, i,
                             s, j,
                             t, k)

    def _export_g_i(self, g, i):
        if i > 0:
            self.printer.group(g[0], i)
        for j, s in enumerate(g[1]):
            self._export_s_j(g, i,
                             s, j)

    # these are for external use

    def _export_all(self):
        for i, g in enumerate(self.index):
            self._export_g_i(g, i)

    def _export_group(self, group):
        for i, g in enumerate(self.index):
            if g[0] == group:
                self._export_g_i(g, i)
                break

    def _export_subgroup(self, group, subgroup):
        for i, g in enumerate(self.index):
            if g[0] == group:
                for j, s in enumerate(g[1]):
                    if s[0] == subgroup:
                        self._export_s_j(g, i,
                                         s, j,
                                         True)
                        break
                break

    def _export_task(self, group, subgroup, task):
        for i, g in enumerate(self.index):
            if g[0] == group:
                for j, s in enumerate(g[1]):
                    if s[0] == subgroup:
                        for k, t in enumerate(s[1]):
                            if t == task:
                                self._export_t_k(g, i,
                                                 s, j,
                                                 t, k,
                                                 True)
                                break
                        break
                break

    # ===========================================
    # Parsers

    def _current_idxs(self):
        group_idx, subgroup_idx = None, None

        if self.current_group is not None:
            for i, g in enumerate(self.index):
                if g[0] == self.current_group:
                    group_idx = i
                    break
            if self.current_subgroup is not None:
                for j, s in enumerate(g[1]):
                    if s[0] == self.current_subgroup:
                        subgroup_idx = j
                        break
        return group_idx, subgroup_idx

    @staticmethod
    def _idxs_to_names(idxs, index):
        if len(idxs) < 3:
            raise DitException("Invalid index format.")

        names = [None] * 3

        try:
            for i, idx in enumerate(idxs):
                if idx is None:  # we can no longer navigate the index; stop
                    break
                idx = int(idx)
                if i < 2:                     # its a group or subgroup
                    names[i] = index[idx][0]
                    index = index[idx][1]     # navigate the index further
                else:                         # its a task
                    names[i] = index[idx]

        except ValueError:
            raise DitException(
                "Invalid index format, must be an integer: %s" % idx)
        except IndexError:
            raise DitException("Invalid index: %d" % idx)

        return names

    def _gid_parser(self, selection):
        idxs = selection.split(SEPARATOR_CHAR)
        if len(idxs) > 3:
            raise DitException("Invalid <gid> format.")

        # replaces missing subgroup or task with None
        idxs = idxs + [None] * (3 - len(idxs))

        return self._idxs_to_names(idxs, self.index)

    def _id_parser(self, selection):
        idxs = selection.split(SEPARATOR_CHAR)
        if len(idxs) > 3:
            raise DitException("Invalid <id> format.")

        # replaces missing group or subgroup with current
        group_idx, subgroup_idx = self._current_idxs()
        if len(idxs) == 1:
            idxs = [group_idx, subgroup_idx] + idxs
        elif len(idxs) == 2:
            idxs = [group_idx] + idxs

        return self._idxs_to_names(idxs, self.index)

    def _gname_parser(self, selection):
        names = selection.split(SEPARATOR_CHAR)
        if len(names) > 3:
            raise DitException("Invalid <gname> format.")
        names = [name if name != ROOT_NAME_CHAR else ROOT_NAME
                 for name in names]
        names = names + [None] * (3 - len(names))
        group, subgroup, task = names

        for name in [group, subgroup]:
            if name and not is_valid_group_name(name):
                raise DitException("Invalid group name: %s" % name)
        if task and not is_valid_task_name(task):
            raise DitException("Invalid task name: %s" % task)

        if group == ROOT_NAME and subgroup:
            group, subgroup = subgroup, (ROOT_NAME if task else None)

        return (group, subgroup, task)

    def _name_parser(self, selection):
        names = selection.split(SEPARATOR_CHAR)
        if len(names) > 3:
            raise DitException("Invalid <name> format.")
        names = [name if name != ROOT_NAME_CHAR else ROOT_NAME
                 for name in names]
        names = [None] * (3 - len(names)) + names

        group, subgroup, task = names

        if group is None:
            if self.current_group is not None:
                group = self.current_group
            else:
                group = ROOT_NAME

        if subgroup is None:
            if self.current_subgroup is not None:
                subgroup = self.current_subgroup
            else:
                subgroup = ROOT_NAME

        for name in [group, subgroup]:
            if not is_valid_group_name(name):
                raise DitException("Invalid group name: %s" % name)
        if not is_valid_task_name(task):
            raise DitException("Invalid task name: %s" % task)

        if group == ROOT_NAME and subgroup:
            group, subgroup = subgroup, group

        return (group, subgroup, task)

    def _backward_parser(self, argv):
        group, subgroup, task = self._get_current()

        if len(argv) > 0 and not argv[0].startswith("-"):
            selection = argv.pop(0)

            if selection == CURRENT_FN:
                task = self.current_task

            elif selection[0].isdigit():
                (group, subgroup, task) = self._id_parser(selection)

            else:
                (group, subgroup, task) = self._name_parser(selection)

        msg_selected(group, subgroup, task)

        if not task:
            raise NoTaskSpecifiedCondition("No task specified.")

        return (group, subgroup, task)

    def _forward_parser(self, argv):
        selection = argv.pop(0)

        if selection == CURRENT_FN:
            return self._get_current()

        elif selection[0].isdigit():
            return self._gid_parser(selection)

        elif not selection.startswith("-"):
            return self._gname_parser(selection)

    # ===========================================
    # Commands

    @command("n", "-: --:", SELECT_BY_NAME)
    def new(self, argv):
        if len(argv) < 1:
            raise ArgumentException("Missing argument.")

        (group, subgroup, task) = self._name_parser(argv.pop(0))
        msg_selected(group, subgroup, task)

        description = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            description = argv.pop(0)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if description is None:
            description = prompt('Description')

        self._create_task(group, subgroup, task, description)
        msg_normal("Created: %s" % _(group, subgroup, task))

        return (group, subgroup, task)

    @command("w", "--new", SELECT_BY_NAME)
    def workon(self, argv):
        if len(argv) < 1:
            raise ArgumentException("Missing argument.")

        if argv[0] in ["--new", "-n"]:
            argv.pop(0)
            (group, subgroup, task) = self.new(argv)
        else:
            (group, subgroup, task) = self._backward_parser(argv)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if not self.current_halted:
            msg_verbose("Already working in a task.")
            return

        data = self._load_task_data(group, subgroup, task)

        previous_updated = False
        if not self._is_current(group, subgroup, task):
            if self.current_task is not None:
                self._previous_add(self.current_group,
                                   self.current_subgroup,
                                   self.current_task)
                previous_updated = True
            if state(data) == State.HALTED:
                self._previous_remove(group, subgroup, task)
                previous_updated = True

        data_clock_in(data)
        msg_normal("Working on: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

        if previous_updated:
            self._save_previous()

        self._set_current(group, subgroup, task)
        self._save_current()

    @command("h", "", SELECT_BY_NAME)
    def halt(self, argv, conclude=False, cancel=False):
        try:
            (group, subgroup, task) = self._backward_parser(argv)
        except NoTaskSpecifiedCondition:
            msg_verbose('Nothing to halt.')
            return

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        data = self._load_task_data(group, subgroup, task)

        task_state = state(data)
        if task_state != State.DOING:
            if not conclude:
                msg_verbose('Not working in task (in %s state).' %
                            task_state.name)
                return
            elif task_state == State.CONCLUDED:
                msg_verbose('Task has already been concluded.')
                return

        if cancel:
            data_clock_cancel(data)
            msg_normal("Canceled: %s" % _(group, subgroup, task))
        else:
            data_clock_out(data)
            msg_normal("Halted: %s" % _(group, subgroup, task))
        if conclude:
            data_conclude(data)
            msg_normal("Concluded: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

        if self._is_current(group, subgroup, task):
            if conclude:
                if not self._previous_empty():
                    group, subgroup, task = self._previous_pop()
                    self._save_previous()
                    self._set_current(group, subgroup, task, True)
                else:
                    self._clear_current()
            else:
                self.current_halted = True
            self._save_current()
        else:
            self._previous_remove(group, subgroup, task)
            self._save_previous()

    @command("a", "", SELECT_BY_NAME)
    def append(self, argv):
        try:
            (group, subgroup, task) = self._backward_parser(argv or
                                                            [CURRENT_FN])
        except NoTaskSpecifiedCondition:
            msg_verbose('No task selected.')
            return

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        data = self._load_task_data(group, subgroup, task)
        task_state = state(data)

        if task_state != State.HALTED:
            msg_verbose("Task is in %s state." % task_state.name)
            return

        if self._is_current(group, subgroup, task):
            data_clock_append(data)
            msg_normal("Continuing: %s" % _(group, subgroup, task))
            self._save_task(group, subgroup, task, data)
            self.current_halted = False
            self._save_current()
        else:
            msg_verbose("Task is not current.")

    @command("x", "", SELECT_BY_NAME)
    def cancel(self, argv):
        self.halt(argv, cancel=True)

    @command("r", "", None)
    def resume(self, argv):
        self.workon([CURRENT_FN])

    @command("s", "--new", SELECT_BY_NAME)
    def switchto(self, argv):
        self.halt([])
        self.workon(argv)

    @command("b", "", None)
    def switchback(self, argv):
        if self._previous_empty():
            msg_verbose("No halted tasks to switchback")
        else:
            self.halt([])
            group, subgroup, task = self._previous_pop()
            self.workon(["%s/%s/%s" % (group, subgroup, task,)])

    @command("c", "", SELECT_BY_NAME)
    def conclude(self, argv):
        self.halt(argv, conclude=True)

    @command("q", "--concluded --verbose --all", SELECT_BY_GNAME)
    def status(self, argv):
        self.export(argv, statussing=True)

    @command("l", "--concluded --verbose --all", SELECT_BY_GNAME)
    def list(self, argv):
        self.export(argv, listing=True)

    @command("e", "--concluded --verbose --all --output", SELECT_BY_GNAME)
    def export(self, argv, listing=False, statussing=False):
        all = False
        output = None

        options = {'concluded': False,
                   'verbose': False}

        if statussing:
            group = None
            subgroup = None
        else:
            group = self.current_group
            subgroup = self.current_subgroup
        task = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--concluded", "-c"]:
                options['concluded'] = True
            elif opt in ["--verbose", "-v"]:
                options['verbose'] = True
            elif opt in ["--all", "-a"]:
                all = True
            elif opt in ["--output", "-o"] and not (listing or statussing):
                output = argv.pop(0)
            else:
                raise ArgumentException("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._forward_parser(argv)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % opt)

        if statussing and group is None:
            group, subgroup, task = self._get_current()

        if statussing and task:
            options['concluded'] = True

        msg_selected(group, subgroup, task)

        if output in [None, "stdout"]:
            file = sys.stdout
            fmt = 'dit'
        else:
            file = open(output, 'w')
            fmt = output.split(".")[-1]

        if fmt not in ['dit', 'org']:
            raise DitException("Unrecognized format: %s", fmt)

        self.printer = import_module('dit.' + fmt + 'printer')
        self.printer.setup(file, options, statussing, listing)

        self.printer.begin()

        if all:
            self._export_all()
        elif task:
            self._export_task(group, subgroup, task)
        elif subgroup is not None:
            self._export_subgroup(group, subgroup)
        elif group is not None:
            self._export_group(group)
        else:
            self._export_all()

        self.printer.end()

        file.close()

    @command("t", "-: --:", SELECT_BY_NAME)
    def note(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        note_text = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            note_text = argv.pop(0)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if note_text is None:
            note_text = prompt("Description")

        if not note_text:
            msg_normal("Operation cancelled.")
            return

        data = self._load_task_data(group, subgroup, task)
        data_add_note(data, note_text)
        msg_normal("Noted added to: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

    @command("p", "-: --:", SELECT_BY_NAME)
    def set(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        prop_name = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            prop_name = argv.pop(0)
            if len(argv) > 0:
                prop_value = argv.pop(0)
            else:
                prop_value = prompt("Value for '%s'" % prop_name)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if prop_name is None:
            prop = prompt("Name and Value for property").split('\n', 1)
            prop_name = prop[0].strip()
            if len(prop) == 2:
                prop_value = prop[1].strip()
            else:
                prop_value = ''

        if not prop_name:
            msg_normal("Operation cancelled.")
            return

        data = self._load_task_data(group, subgroup, task)
        data_set_property(data, prop_name, prop_value)
        msg_normal("Set property of: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

    @command("m", "", SELECT_BY_NAME)
    def edit(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        data_pretty = json.dumps(self._load_task_data(group, subgroup, task),
                                 indent=4)
        header = "Editing: " + _(group, subgroup, task)

        new_data_raw = prompt(header, data_pretty, "json")

        if new_data_raw:
            new_data = json.loads(new_data_raw)
            if is_valid_task_data(new_data):
                msg_normal("Manually edited: %s" % _(group, subgroup, task))
                self._save_task(group, subgroup, task, new_data)
            else:
                msg_normal("Invalid data type, should be a dictionary.")
        else:
            msg_normal("Operation cancelled.")

    @command("", "", None)
    def rebuild_index(self, argv):
        self._rebuild_index()
        self._save_index()

    # ===========================================
    # Main

    def configure(self, argv):
        global VERBOSE
        directory = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                VERBOSE = True
            elif opt in ["--directory", "-d"]:
                directory = argv.pop(0)
            elif opt in ["--help", "-h"]:
                msg_usage()
                return False
            else:
                raise ArgumentException("No such option: %s" % opt)

        self._setup_base_path(directory)
        self._load_current()
        self._load_previous()
        self._load_index()
        return True

    def interpret(self, argv):
        if len(argv) > 0:
            cmd = argv.pop(0)
            if cmd in COMMAND_INFO:
                getattr(self, COMMAND_INFO[cmd]['name'])(argv)
            else:
                raise ArgumentException("No such command: %s" % cmd)
        else:
            raise ArgumentException("Missing command.")

# ===========================================
# Completion


def completion_gname(dit, names):

    names[-1] = None
    names = names + [None] * (3 - len(names))
    group, subgroup, task = names

    comp_options = []
    for i, g in enumerate(dit.index):
        if group is None:
            comp_options.append(_(g[0]) + SEPARATOR_CHAR)
        elif g[0] == group:
            for j, s in enumerate(g[1]):
                if subgroup is None:
                    comp_options.append(_(g[0], s[0]) + SEPARATOR_CHAR)
                elif s[0] == subgroup:
                    for k, t in enumerate(s[1]):
                        comp_options.append(_(g[0], s[0], t))
                    break
            break

    return '\n'.join(comp_options)


def completion_selection(cmd, directory, selection):

    names = selection.split(SEPARATOR_CHAR)
    names = [name if name != ROOT_NAME_CHAR else ROOT_NAME for name in names]
    if len(names) > 3:
        return ""

    dit = Dit()
    path = discover_base_path(directory)
    if not os.path.exists(path):
        return ""

    dit.base_path = path
    dit._load_index()
    if not dit.index:
        return ""

    select = COMMAND_INFO[cmd]['select']

    if select in [SELECT_BY_GNAME, SELECT_BY_NAME]:
        return completion_gname(dit, names)
    else:
        return ""


def completion_cmd_name():
    return '\n'.join([cmd for cmd in COMMAND_INFO])


def completion_cmd_option(cmd):
    return COMMAND_INFO[cmd]['options']


def completion_option():
    return "--verbose\n--directory\n--help"


def completion():
    argv = sys.argv
    argv.pop(0)

    idx = int(argv.pop(0)) - 1
    line = argv[1:]
    cmd = None
    directory = None

    i = 0
    while i != idx and i < len(line):
        if line[i] in ["--directory", "-d"]:
            i += 1
            directory = line[i]
        elif line[i].isalpha():
            cmd = line[i]
            break
        i += 1

    if cmd and cmd not in COMMAND_INFO:
        return ""

    word = line[idx] if len(line) > idx else ""

    if word == "" or word[0].isalpha():
        if cmd:
            comp_options = completion_selection(cmd, directory, word)
        else:
            comp_options = completion_cmd_name()
    elif word.startswith((ROOT_NAME_CHAR, SEPARATOR_CHAR)):
        if cmd:
            comp_options = completion_selection(cmd, directory, word)
        else:
            comp_options = ""
    elif word.startswith('-'):
        if cmd:
            comp_options = completion_cmd_option(cmd)
        else:
            comp_options = completion_option()
    else:
        comp_options = ""

    sys.stdout.write(comp_options)

# ===========================================
# Main


def main():
    argv = sys.argv
    argv.pop(0)

    dit = Dit()
    try:
        if dit.configure(argv):
            dit.interpret(argv)
    except DitException as err:
        msg_error(err)
    except IndexError as err:
        # this was probably caused by a pop on an empty argument list
        msg_error("Missing argument.")
    except json.decoder.JSONDecodeError:
        msg_error("Invalid JSON.")
