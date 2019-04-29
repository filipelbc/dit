# -*- coding: utf-8 -*-

"""
Version 0.7.3

Usage: dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. If not specified, the
    closest ".dit" directory in the tree is used. If not found, "~/.dit" is
    used. The selected directory will be refered to as "dit directory".

  --verbose, -v
    Prints detailed information of what is being done.

  --help, -h
    Prints this message and quits.

  --check-hooks
    Stop with error when hook process fails.

  --no-hooks
    Disable the use of hooks.

  Workflow <command>'s:

    new [--fetch, -f] <name> ["title"]
      Creates a new task. You will be prompted for the "title" if it is
      not provided.
      --fetch, -n
        Use data fetcher plugin.

    workon <id> | <name> | --new, -n [--fetch, -f] <name> ["title"]
      Starts clocking the specified task. If already working on a task, nothing
      is done. Sets the CURRENT and PREVIOUS tasks.
      --at, -a "date"
        Use the datetime given by "date" instead of now.
      --new, -n
        Same as "new" followed by "workon".

    halt
      Stops clocking the CURRENT task.
      --at, -a "date"
        Use the datetime given by "date" instead of now.

    append
      Undoes the previous "halt".

    cancel
      Undoes the previous "workon" (but the CURRENT task is not changed back).

    resume
      Same as "workon CURRENT".

    switchto <id> | <name> | --new, -n [--fetch, -f] <name> ["title"]
      Same as "halt" followed by "workon".

    switchback
      Same as "halt" followed by "workon PREVIOUS". If there is no PREVIOUS
      task, nothing is done.

    conclude [<id> | <name>]
      Concludes the CURRENT task or the selected one. Implies a "halt". It may
      set the CURRENT and/or PREVIOUS tasks.

  Listing <command>'s:

    export [--all, -a] [--concluded, -c] [--compact, -z]
           [--output, -o "file"] [--format, -f "format"] [<gid> | <gname>]
      Prints most information of the CURRENT subgroup or the selected one.
      --all, -a
        Select all groups and subgroups.
      --concluded, -c
        Include concluded tasks.
      --compact, -z
        Make the output more compact.
      --output, -o "file-name"
        File to which to write. Defaults to "stdout".
      --format, -f "format"
        Format to use. If not provided, the format is deduced from the file
        extension if present, else it defaults to dit's own format.

      For a given format, dit will try to use an external exporter plugin
      first. It will fallback to an internal exporter if possible or fail if
      none found.

    list
      This is a convenience alias for "export --output stdout --format dit".

    status
      Prints an overview of the data for the CURRENT and PREVIOUS tasks.

    Note that these commands also accept the following options:
    --verbose, -v
      More information is shown.
    --sum, -s
      Show the overall time spent on the listed tasks.
    --from "date"
      Only consider tasks and log entries from the given date on.
    --to "date"
      Only consider tasks and log entries up to the given date.
    --where, -w "property-name" "property-value"
      Only consider tasks that have the given property with the given value.
      Note that the value can be a regular expression.

  Task editing <command>'s:

    fetch <name>
      Use data fetcher plugin.

    move [--fetch, -f] <name> <name>
      Rename task or change its group and/or subgroup.
      --fetch, -f
        Use data fetcher plugin after moving.

    note [--task, -t <name> | <id>] ["text"]
      Adds a note to the CURRENT task or the specified one. You will be
      prompted for the "text" if it is not provided.

    set [--task, -t <name> | <id>] ["name" ["value"]]
      Sets a property for the CURRENT task or the specified one. You will be
      prompted for the "name" and "value" if they're not provided.

    edit [<name> | <id>]
      Opens the specified task for manual editing. Uses CURRENT task or the
      specified one. It will look in environment variables $VISUAL and $EDITOR
      for a text editor to use and if none is found it will do nothing.

  Other <command>'s:

    rebuild-index
      Rebuild the ".index" file. For use in case of manual modification of the
      contents of the dit directory.

  Plugins:

    Data fetcher:
      This allows placing a script named ".fetcher" in the directory
      of a group or subgroup, which will be used for fetching data for the task
      from an external source. It will be called in the following manner:
        "$ .fetcher dit-directory group subgroup task"
      It should save the fetched data in the file:
        "dit-directory/group/subgroup/task.json"

    Exporter:
      This allows specifying custom formats for the export command.
      The plugin should be installed as a Python module whose name has the
      following format "dit_Xexporter" where "X" will be the format specified
      by "--format X" in the export command call.
      The following methods should be available in the module:
        - setup(file, options)
        - begin()
        - end()
        - group(group, group_id)
        - subgroup(group, group_id, subgroup, subgroup_id)
        - task(group, group_id, subgroup, subgroup_id, task, task_id, data)

    Hooks:
      Hooks are scripts that can be called before and after a command. The
      following hooks are available:
        - "before": called before any command
        - "(before|after)_write": called before/after any command that modifies
                                  some task file (non-listing commands)
        - "(before|after)_read": called before/after any readonly command
                                 (listing commands)
        - "after": called after any command is executed successfully.
      The script should be installed in the ".hooks" directory in your dit
      directory and it will be called in the following manner:
        "$ hook-name dit-directory command-name"

  Clarifications:

  When mandatory arguments are not provided, you will be prompted to provide
  them.  This will either be done by opening a  text editor or with a simple
  CLI prompt. The editor will be used if either the $VISUAL or $EDITOR
  environment variable is set.

  <name>: [["group-name"/]"subgroup-name"/]"task-name" | CURRENT | PREVIOUS

  <gname>: "group-name"[/"subgroup-name"[/"task-name"]] | CURRENT | PREVIOUS

  CURRENT is a reference to the most recent task that received a "workon"
  and has not been "concluded". PREVIOUS is a reference to the second most
  recent.

  Note that a "*-name" must begin with a letter to be valid. Group- and
  subgroup-names can be empty or a ".", which means no group and/or subgroup.

  Also note that CURRENT and PREVIOUS are not valid arguments for the command
  "new".

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
from importlib.util import find_spec
from tempfile import gettempdir

from . import messages as msg

from .exceptions import (
    DitError,
    ArgumentError,
    NoTaskSpecifiedError,
    SubprocessError,
    maybe_raise_unrecognized_argument,
)
from .utils import now_str, interpret_date, dt2str

from .common import (
    CURRENT,
    CURRENT_FN,
    FETCHER_FN,
    HOOKS_DIR,
    PREVIOUS,
    PREVIOUS_FN,
    ROOT_NAME,
    SELECT_BACKWARD,
    SELECT_FORWARD,
    discover_base_path,
    is_valid_task_name,
    load_json_file,
    names_to_string,
    path_to_string,
    save_json_file,
    selector_split,
)

from .index import Index

# ===========================================
# Constants

COMMENT_CHAR = "#"

# ===========================================
# Enumerators


class State(Enum):
    TODO = 1
    DOING = 2
    HALTED = 3
    CONCLUDED = 4

# ===========================================
# General Options


HOOKS_ENABLED = True
CHECK_HOOKS = False

# ===========================================
# System


def get_system_editor():
    # preference to the visual editor
    editor = os.environ.get('VISUAL')
    if not editor:
        editor = os.environ.get('EDITOR')
    return editor


def run_subprocess(*args, **kwargs):
    if not sys.stdout.isatty():
        sys.stdout.flush()
    return subprocess.run(*args, **kwargs)


def load_plugin(plugin_name):
    external = "dit_%s" % plugin_name
    if find_spec(external):
        return import_module(external)
    internal = "dit.%s" % plugin_name
    if find_spec(internal):
        return import_module(internal)
    raise DitError("Plugin module not found: %s "
                   "Your dit installation might be corrupt."
                   % plugin_name)

# ===========================================
# Command decorator


COMMAND_INFO = {}

FILTER_OPTIONS = [
    "--verbose",
    "--id-only",
    "--name-only",
    "--sum",
    "--from",
    "--to",
    "--where",
]

LIST_OPTIONS = FILTER_OPTIONS + [
    "--all",
    "--concluded",
    "--compact",
]


def command(letter=None, options=[], select=None, readonly=False):
    def wrapper(cmd):
        global COMMAND_INFO
        name = cmd.__name__.replace("_", "-")
        if name in COMMAND_INFO:
            raise Exception("Method `%s` is already registered as command." % name)
        COMMAND_INFO[name] = {'name': cmd.__name__,
                              'letter': letter,
                              'options': options,
                              'select': select,
                              'readonly': readonly}
        if letter and letter in COMMAND_INFO:
            raise Exception("Letter `%s` is already registered as command." % letter)
        if letter:
            COMMAND_INFO[letter] = COMMAND_INFO[cmd.__name__]
        return cmd
    return wrapper

# ===========================================
# To Nice String


_ = names_to_string


def msg_selected(group, subgroup, task):
    msg.verbose("Selected: %s" % _(group, subgroup, task))

# ==========================================
# Selector


ID_SELECTOR = "id"
GID_SELECTOR = "gid"
NAME_SELECTOR = "name"
GNAME_SELECTOR = "gname"


def selector_to_tuple(string, kind=NAME_SELECTOR):
    sel = selector_split(string)
    if len(sel) > 3:
        raise DitError("Invalid <%s> format." % kind)
    if kind in [ID_SELECTOR, NAME_SELECTOR]:
        sel = [None] * (3 - len(sel)) + sel
    else:
        sel = sel + [None] * (3 - len(sel))
    return sel

# ===========================================
# I/O


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        msg.verbose("Created: %s" % path_to_string(path))


def make_tmp_fp(name, extension):
    name = re.sub(r'[^_A-Za-z0-9]', '_', name).strip('_') + '.' + extension

    path = os.path.join(gettempdir(), getuser(), "dit")
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.join(path, name)


def prompt(header, initial=None, extension='txt'):
    editor = get_system_editor()
    if sys.stdout.isatty():
        if editor:
            input_fp = make_tmp_fp(header, extension)
            with open(input_fp, 'w') as f:
                f.write(COMMENT_CHAR + ' ' + header + '\n')
                if initial:
                    f.write(initial)
            try:
                run_subprocess([editor, input_fp], check=True)
            except subprocess.CalledProcessError:
                raise SubprocessError("%s %s" % (editor, input_fp))
            with open(input_fp, 'r') as f:
                lines = [line for line in f.readlines()
                         if not line.startswith(COMMENT_CHAR)]
            return (''.join(lines)).strip()

        elif not initial:
            return input(header + ': ').strip()
        else:
            raise DitError("Could not find the text editor to use.")
    else:
        raise DitError('Cannot prompt while not running interactively.')

# ===========================================
# Task Verification


def is_valid_group_name(name):
    return name == ROOT_NAME or is_valid_task_name(name)


def is_valid_task_data(data):
    if not isinstance(data, dict):
        msg.warning("Expected data to be a `dict` but got a `%s`."
                    % data.__class__.__name__)
        return False
    types = {
        'properties': dict,
        'logbook': list,
        'notes': list,
        'title': str,
    }
    ans = True
    for key in sorted(types.keys() & data.keys()):
        if not isinstance(data[key], types[key]):
            msg.warning("Expected `data.%s` to be a `%s` but got a `%s`."
                        % (key,
                           types[key].__name__,
                           data[key].__class__.__name__))
            ans = False
    return ans

# ===========================================
# Task Data Manipulation


NEW_TASK_DATA = {
    "title": None,
    "logbook": [],
    "properties": {},
    "notes": [],
    "created_at": None,
}


def state(task_data):
    if task_data.get('concluded_at'):
        return State.CONCLUDED
    logbook = task_data.get('logbook', [])
    if len(logbook) > 0:
        last = logbook[-1]
        if last['out']:
            return State.HALTED
        else:
            return State.DOING
    else:
        return State.TODO


def data_clock_in(data, at=None):
    logbook = data.get('logbook', [])
    if len(logbook) > 0:
        last = logbook[-1]
        if not last['out']:
            msg.normal("Already clocked in.")
            return
    data.pop('concluded_at', None)
    data['logbook'] = logbook + [{'in': at or now_str(), 'out': None}]


def data_clock_append(data):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg.normal("Task has no been clocked yet.")
        return
    last = logbook[-1]
    if not last['out']:
        msg.normal("Already clocked in.")
        return
    last['out'] = None


def data_clock_out(data, at=None):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg.normal("Task has no been clocked yet.")
        return
    last = logbook[-1]
    if last['out']:
        msg.normal("Already clocked out.")
        return
    last['out'] = at or now_str()
    data['logbook'] = logbook


def data_clock_cancel(data):
    logbook = data.get('logbook', [])
    if len(logbook) == 0:
        msg.normal("Task has no been clocked yet.")
        return
    last = logbook[-1]
    if last['out']:
        msg.normal("Was not clocked in.")
        return
    logbook.pop(-1)
    data['logbook'] = logbook


def data_conclude(data, at=None):
    if data.get('concluded_at'):
        msg.normal("Already concluded.")
        return
    data['concluded_at'] = at or now_str()


def data_add_note(data, note_text):
    if 'notes' not in data:
        data['notes'] = []
    data['notes'].append(note_text)


def data_set_property(data, prop_name, prop_value):
    if 'properties' not in data:
        data['properties'] = {}

    properties = data['properties']
    if prop_name in properties:
        if not msg.yn_question('Property `%s` already exists with value: %s\n'
                               'Do you want to overwrite?' %
                               (prop_name, properties[prop_name])):
            return False
    properties[prop_name] = prop_value
    return True


def data_update(current, other):
    other.pop('logbook', [])  # do not merge logbook!

    for key in other:
        if key in current:
            if key == 'properties':
                current[key].update(other[key])
            elif key == 'notes':
                current[key] += other[key]
            else:
                current[key] = other[key]
        else:
            current[key] = other[key]

    return current

# ===========================================
# Dit Class


class Dit:

    current_group = None
    current_subgroup = None
    current_task = None
    current_halted = True

    previous_stack = []

    index = Index()

    base_path = None
    exporter = None

    # ===========================================
    # Paths and files names

    def _setup_base_path(self, directory):
        path = discover_base_path(directory)
        make_dirs(path)
        msg.verbose("Using directory: %s" % path_to_string(path))
        self.base_path = path

    def _current_path(self):
        return os.path.join(self.base_path, CURRENT_FN)

    def _previous_path(self):
        return os.path.join(self.base_path, PREVIOUS_FN)

    def _hook_path(self, hook):
        return os.path.join(self.base_path, HOOKS_DIR, hook)

    def _plugin_path(self, name, group, subgroup):
        try_paths = [
            os.path.join(self.base_path, group, subgroup, name),
            os.path.join(self.base_path, group, name),
            os.path.join(self.base_path, name),
        ]
        for path in try_paths:
            if os.path.isfile(path):
                return path
        return None

    def _raise_task_exists(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup, task)
        if os.path.exists(path):
            raise DitError("Task already exists: %s" % path)

    def _get_task_path(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup, task)
        if not os.path.isfile(path):
            raise DitError("No such task file: %s" % path)
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

    def _load_task_data(self, group, subgroup, task):
        task_fp = self._get_task_path(group, subgroup, task)
        data = load_json_file(task_fp)
        if not is_valid_task_data(data):
            raise DitError("Task file contains invalid data: %s"
                           % task_fp)
        return data

    def _save_task(self, group, subgroup, task, data):
        task_fp = self._make_task_path(group, subgroup, task)
        data['updated_at'] = now_str()
        save_json_file(task_fp, data)
        msg.verbose("Task saved: %s" % _(group, subgroup, task))

    def _create_task(self, group, subgroup, task, data):
        task_fp = self._make_task_path(group, subgroup, task)
        data['created_at'] = now_str()
        save_json_file(task_fp, data)
        self.index.add(group, subgroup, task)
        self.index.save()

    # Current Task

    def _get_current(self):
        return (self.current_group,
                self.current_subgroup,
                None if self.current_halted else self.current_task)

    def _get_current_task(self):
        return (self.current_group,
                self.current_subgroup,
                self.current_task)

    def _clear_current(self):
        self._set_current(None, None, None, True)

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
        msg.verbose("%s saved: %s%s"
                    % (CURRENT,
                       _(self.current_group,
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
    def _previous_empty(self):
        return len(self.previous_stack) == 0

    def _previous_add(self, group, subgroup, task):
        s = _(group, subgroup, task)
        self.previous_stack.append(s)

    def _previous_remove(self, group, subgroup, task):
        s = _(group, subgroup, task)
        self.previous_stack = [i for i in self.previous_stack if i != s]

    def _previous_pop(self):
        return selector_split(self.previous_stack.pop())

    def _previous_peek(self):
        if self._previous_empty():
            return (None, None, None)
        return selector_split(self.previous_stack[-1])

    def _save_previous(self):
        save_json_file(self._previous_path(), self.previous_stack)
        l = len(self.previous_stack)
        msg.verbose("%s saved. It has %d task%s now."
                    % (PREVIOUS, l, "s" if l != 1 else ""))

    def _load_previous(self):
        previous = load_json_file(self._previous_path())
        if previous is not None:
            self.previous_stack = previous

    # ===========================================
    # Export

    # these are for internal use

    def _export_t_k(self, g, i, s, j, t, k, force_header=False):
        if not t:
            return
        if force_header:
            if i > 0:
                self.exporter.group(g[0], i)
            if j > 0:
                self.exporter.subgroup(g[0], i, s[0], j)

        data = self._load_task_data(g[0], s[0], t)
        self.exporter.task(g[0], i, s[0], j, t, k, data)

    def _export_s_j(self, g, i, s, j, force_header=False):
        if force_header and i > 0:
            self.exporter.group(g[0], i)

        if j > 0:
            self.exporter.subgroup(g[0], i, s[0], j)
        for k, t in enumerate(s[1]):
            self._export_t_k(g, i,
                             s, j,
                             t, k)

    def _export_g_i(self, g, i):
        if i > 0:
            self.exporter.group(g[0], i)
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
                                return True
        return False

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

    def _gid_parser(self, string):
        idxs = selector_to_tuple(string, GID_SELECTOR)
        return self.index.idxs_to_names(idxs)

    def _id_parser(self, string):
        idxs = selector_to_tuple(string, ID_SELECTOR)

        # replaces missing group or subgroup with current
        group_idx, subgroup_idx = self._current_idxs()
        if idxs[0] is None:
            idxs[0] = group_idx
        if idxs[1] is None:
            idxs[1] = subgroup_idx

        return self.index.idxs_to_names(idxs)

    def _gname_parser(self, string):
        (group, subgroup, task) = selector_to_tuple(string, GNAME_SELECTOR)

        for name in [group, subgroup]:
            if name and not is_valid_group_name(name):
                raise DitError("Invalid group name: %s" % name)
        if task and not is_valid_task_name(task):
            raise DitError("Invalid task name: %s" % task)

        if group == ROOT_NAME and subgroup:
            group, subgroup = subgroup, (ROOT_NAME if task else None)

        return (group, subgroup, task)

    def _name_parser(self, string):
        (group, subgroup, task) = selector_to_tuple(string, NAME_SELECTOR)

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
                raise DitError("Invalid group name: %s" % name)
        if not is_valid_task_name(task):
            raise DitError("Invalid task name: %s" % task)

        if group == ROOT_NAME and subgroup:
            group, subgroup = subgroup, group

        return (group, subgroup, task)

    def _backward_parser(self, argv, throw=True, require_prefix=False):
        (group, subgroup, task) = self._get_current()

        selection = None
        if len(argv) > 0:
            if require_prefix:
                if argv[0] in ["--task", "-t"]:
                    argv.pop(0)
                    selection = argv.pop(0)
            elif not argv[0].startswith("-"):
                selection = argv.pop(0)

        if selection is not None:

            if selection == CURRENT:
                task = self.current_task

            elif selection == PREVIOUS:
                (group, subgroup, task) = self._previous_peek()

            elif selection[0].isdigit():
                (group, subgroup, task) = self._id_parser(selection)

            else:
                (group, subgroup, task) = self._name_parser(selection)

        msg_selected(group, subgroup, task)
        if not task and throw:
            raise NoTaskSpecifiedError("No task specified.")
        return (group, subgroup, task)

    def _forward_parser(self, argv):
        selection = argv.pop(0)

        if selection == CURRENT:
            (group, subgroup, task) = self._get_current()

        elif selection == PREVIOUS:
            (group, subgroup, task) = self._previous_peek()

        elif selection[0].isdigit():
            (group, subgroup, task) = self._gid_parser(selection)

        elif not selection.startswith("-"):
            (group, subgroup, task) = self._gname_parser(selection)

        return (group, subgroup, task)

    # ===========================================
    # Hooks

    def _call_hook(self, hook, cmd_name):
        if HOOKS_ENABLED:
            hook_fp = self._hook_path(hook)
            if os.path.isfile(hook_fp):
                msg.verbose("Executing hook: %s" % hook)
                try:
                    run_subprocess([hook_fp, self.base_path, cmd_name],
                                   check=CHECK_HOOKS)
                except subprocess.CalledProcessError:
                    raise SubprocessError(hook_fp)

    def _fetch_data_for(self, group, subgroup, task):
        fetcher_fp = self._plugin_path(FETCHER_FN, group, subgroup)
        if not fetcher_fp:
            raise DitError("Data fetcher script `%s` not found."
                           % FETCHER_FN)
        else:
            msg.verbose("Fetching data with `%s`." % fetcher_fp)

        fetch_fp = self._make_task_path(group, subgroup, task) + ".json"

        try:
            run_subprocess([
                fetcher_fp, self.base_path, _(group), _(subgroup), _(task)
            ], check=True)
        except subprocess.CalledProcessError:
            raise SubprocessError(fetcher_fp)

        if not os.path.isfile(fetch_fp):
            raise DitError("`%s` not found: it seems no data was fetched."
                           % fetch_fp)

        data = load_json_file(fetch_fp)
        if not is_valid_task_data(data):
            raise DitError("Fetched data is invalid: %s" % fetch_fp)
        os.remove(fetch_fp)
        return data

    # ===========================================
    # Commands

    @command("n", ["--fetch"], SELECT_BACKWARD)
    def new(self, argv):
        title = None
        fetch = False

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--fetch", "-f"]:
                fetch = True
            else:
                raise ArgumentError("No such option: %s" % opt)

        if len(argv) < 1:
            raise ArgumentError("Missing argument.")
        (group, subgroup, task) = self._name_parser(argv.pop(0))
        msg_selected(group, subgroup, task)

        if len(argv) > 0:
            title = argv.pop(0)

        maybe_raise_unrecognized_argument(argv)
        self._raise_task_exists(group, subgroup, task)

        data = NEW_TASK_DATA
        if fetch:
            fetched_data = self._fetch_data_for(group, subgroup, task)
            data = data_update(data, fetched_data)

        if not data.get('title'):
            data['title'] = title or prompt('Task title')

        if not data.get('title'):
            msg.normal("Operation cancelled.")
            return None

        self._create_task(group, subgroup, task, data)
        msg.normal("Created: %s" % _(group, subgroup, task))

        return (group, subgroup, task)

    @command("w", ["--at", "--new"], SELECT_BACKWARD)
    def workon(self, argv):
        if len(argv) < 1:
            raise ArgumentError("Missing argument.")

        if not self.current_halted:
            msg.normal("Nothing to do: already working on a task.")
            return

        at = None

        if argv[0] in ["--at", "-a"]:
            argv.pop(0)
            at = dt2str(interpret_date(argv.pop(0)))

        if argv[0] in ["--new", "-n"]:
            argv.pop(0)
            task_tuple = self.new(argv)
            if not task_tuple:
                return
            (group, subgroup, task) = task_tuple
        else:
            (group, subgroup, task) = self._backward_parser(argv)
        maybe_raise_unrecognized_argument(argv)

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

        data_clock_in(data, at)
        msg.normal("Working on: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

        if previous_updated:
            self._save_previous()

        self._set_current(group, subgroup, task)
        self._save_current()

    @command("h", ["--at"])
    def halt(self, argv, conclude=False, cancel=False):
        at = None
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--at", "-a"]:
                at = dt2str(interpret_date(argv.pop(0)))
            else:
                raise ArgumentError("No such option: %s" % opt)

        if conclude:
            (group, subgroup, task) = self._backward_parser(argv or [CURRENT], throw=False)
            maybe_raise_unrecognized_argument(argv)
        else:
            maybe_raise_unrecognized_argument(argv)
            (group, subgroup, task) = self._backward_parser([CURRENT], throw=False)

        if not task:
            msg.normal('Nothing to do: %s.' % ("no task selected" if conclude
                                               else "no current task"))
            return

        data = self._load_task_data(group, subgroup, task)

        task_state = state(data)
        if task_state != State.DOING:
            if not conclude:
                msg.normal('Nothing to do: not working on the task.')
                return
            elif task_state == State.CONCLUDED:
                msg.normal('Nothing to do: task is already concluded.')
                return

        if cancel:
            data_clock_cancel(data)
            msg.normal("Canceled: %s" % _(group, subgroup, task))
        elif task_state == State.DOING:
            data_clock_out(data, at)
            msg.normal("Halted: %s" % _(group, subgroup, task))
        if conclude:
            data_conclude(data, at)
            msg.normal("Concluded: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

        if self._is_current(group, subgroup, task):
            if conclude:
                if self._previous_empty():
                    self._set_current(group, subgroup, None, True)
                else:
                    group, subgroup, task = self._previous_pop()
                    self._save_previous()
                    self._set_current(group, subgroup, task, True)
            else:
                self.current_halted = True
            self._save_current()
        else:
            self._previous_remove(group, subgroup, task)
            self._save_previous()

    @command("a")
    def append(self, argv):
        maybe_raise_unrecognized_argument(argv)

        try:
            (group, subgroup, task) = self._backward_parser([CURRENT])
        except NoTaskSpecifiedError:
            msg.normal('Nothing to do: no current task.')
            return

        data = self._load_task_data(group, subgroup, task)
        task_state = state(data)

        if task_state != State.HALTED:
            msg.normal("Nothing to do: task is not halted.")
            return

        data_clock_append(data)
        msg.normal("Appending to: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)
        self.current_halted = False
        self._save_current()

    @command("x")
    def cancel(self, argv):
        maybe_raise_unrecognized_argument(argv)
        self.halt([], cancel=True)

    @command("r")
    def resume(self, argv):
        maybe_raise_unrecognized_argument(argv)
        self.workon([CURRENT])

    @command("s", ["--new"], SELECT_BACKWARD)
    def switchto(self, argv):
        self.halt([])
        self.workon(argv)

    @command("b")
    def switchback(self, argv):
        maybe_raise_unrecognized_argument(argv)
        if self._previous_empty():
            msg.normal("Nothing to do: no previous task.")
        else:
            self.halt([])
            self.workon([PREVIOUS])

    @command("c", select=SELECT_BACKWARD)
    def conclude(self, argv):
        self.halt(argv, conclude=True)

    @command("q", FILTER_OPTIONS, readonly=True)
    def status(self, argv):
        options = {
            'statussing': True,
            'compact-header': True,
        }
        filters = {}
        limit = 0

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                options['verbose'] = True
            elif opt in ["--id-only", "-i"]:
                options['id-only'] = True
            elif opt in ["--name-only", "-i"]:
                options['name-only'] = True
            elif opt in ["--sum", "-s"]:
                options["sum"] = True
            elif opt in ["--from"]:
                filters["from"] = interpret_date(argv.pop(0))
            elif opt in ["--to"]:
                filters["to"] = interpret_date(argv.pop(0))
            elif opt in ["--where", "-w"]:
                filters["where"] = [argv.pop(0), re.compile(argv.pop(0))]
            elif opt in ["--limit", "-l", "-n"]:
                limit = int(argv.pop(0))
                if limit < 1:
                    limit = 1
            else:
                raise ArgumentError("No such option: %s" % opt)
        maybe_raise_unrecognized_argument(argv)

        if filters:
            options['filters'] = filters

        self.exporter = load_plugin('dit_exporter')
        self.exporter.setup(sys.stdout, options)
        self.exporter.begin()

        (group, subgroup, task) = self._get_current_task()
        self._export_task(group, subgroup, task)

        for i, selection in enumerate(reversed(self.previous_stack)):
            if limit > 0 and i == limit - 1:
                break
            (group, subgroup, task) = selector_split(selection)
            self._export_task(group, subgroup, task)

        self.exporter.end()

    @command("l", LIST_OPTIONS, SELECT_FORWARD, True)
    def list(self, argv):
        self.export(argv, listing=True)

    @command("o", LIST_OPTIONS + ["--output", "--format"], SELECT_FORWARD, True)
    def export(self, argv, listing=False):
        all = False
        output_file = None
        output_format = None

        options = {}
        filters = {}

        group = self.current_group
        subgroup = self.current_subgroup
        task = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                options['verbose'] = True
            elif opt in ["--id-only", "-i"]:
                options['id-only'] = True
            elif opt in ["--name-only", "-i"]:
                options['name-only'] = True
            elif opt in ["--sum", "-s"]:
                options["sum"] = True
            elif opt in ["--from"]:
                filters["from"] = interpret_date(argv.pop(0))
            elif opt in ["--to"]:
                filters["to"] = interpret_date(argv.pop(0))
            elif opt in ["--where", "-w"]:
                filters["where"] = [argv.pop(0), re.compile(argv.pop(0))]
            elif opt in ["--all", "-a"]:
                all = True
            elif opt in ["--concluded", "-c"]:
                options['concluded'] = True
            elif opt in ["--compact", "-z"]:
                options['compact-header'] = True
            elif opt in ["--output", "-o"] and not listing:
                output_file = argv.pop(0)
            elif opt in ["--format", "-f"] and not listing:
                output_format = argv.pop(0)
            else:
                raise ArgumentError("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._forward_parser(argv)
        msg_selected(group, subgroup, task)
        maybe_raise_unrecognized_argument(argv)

        if task:
            options['concluded'] = True

        if filters:
            options['filters'] = filters

        if output_file in [None, "stdout"]:
            exporter_stdout = sys.stdout
        else:
            exporter_stdout = open(output_file, 'w')
            if not output_format:
                __, ext = os.path.splitext(output_file)
                output_format = ext[1:]

        output_format = output_format or 'dit'

        self.exporter = load_plugin("%s_exporter" % output_format)
        self.exporter.setup(exporter_stdout, options)
        self.exporter.begin()

        if all:
            self._export_all()
        elif task:
            if not self._export_task(group, subgroup, task):
                raise DitError('Task not found in index.')
        elif subgroup is not None:
            self._export_subgroup(group, subgroup)
        elif group is not None:
            self._export_group(group)
        else:
            self._export_all()

        self.exporter.end()

        if output_file not in [None, "stdout"]:
            exporter_stdout.close()

    @command("f", [], SELECT_BACKWARD)
    def fetch(self, argv):
        (group, subgroup, task) = self._backward_parser(argv)
        maybe_raise_unrecognized_argument(argv)

        fetched_data = self._fetch_data_for(group, subgroup, task)
        if not fetched_data:
            msg.verbose('Nothing to do: feched data is empty.')
            return

        initial_data = self._load_task_data(group, subgroup, task)
        new_data = data_update(initial_data, fetched_data)
        msg.normal('Fetched data for: %s' % _(group, subgroup, task))
        self._save_task(group, subgroup, task, new_data)

    @command("m", ["--fetch"], SELECT_BACKWARD)
    def move(self, argv):
        fetch = False
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--fetch", "-f"]:
                fetch = True
            else:
                raise ArgumentError("No such option: %s" % opt)
        (from_group, from_subgroup, from_task) = self._name_parser(argv.pop(0))
        (to_group, to_subgroup, to_task) = self._name_parser(argv.pop(0))
        maybe_raise_unrecognized_argument(argv)
        self._raise_task_exists(to_group, to_subgroup, to_task)

        from_fp = os.path.join(self.base_path, from_group, from_subgroup, from_task)

        from_selector = _(from_group, from_subgroup, from_task)
        to_selector = _(to_group, to_subgroup, to_task)

        data = self._load_task_data(from_group, from_subgroup, from_task)
        self._create_task(to_group, to_subgroup, to_task, data)

        os.remove(from_fp)
        msg.normal("Task %s moved to %s" % (from_selector, to_selector))

        # update CURRENT
        if self._is_current(from_group, from_subgroup, from_task):
            self._set_current(to_group, to_subgroup, to_task, self.current_halted)
            self._save_current()

        # update PREVIOUS
        for i in range(0, len(self.previous_stack)):
            if self.previous_stack[i] == from_selector:
                self.previous_stack[i] = to_selector
                self._save_previous()
                break

        # clean INDEX
        self.index.remove(from_group, from_subgroup, from_task)
        self.index.save()

        if fetch:
            self.fetch([to_selector])

    @command("t", [], SELECT_BACKWARD)
    def note(self, argv):
        (group, subgroup, task) = self._backward_parser(argv, require_prefix=True)

        note_text = argv.pop(0) if len(argv) > 0 else None

        maybe_raise_unrecognized_argument(argv)

        if note_text is None:
            note_text = prompt("New note")

        if not note_text:
            msg.normal("Operation cancelled.")
            return

        data = self._load_task_data(group, subgroup, task)
        data_add_note(data, note_text)
        msg.normal("Noted added to: %s" % _(group, subgroup, task))
        self._save_task(group, subgroup, task, data)

    @command("p", [], SELECT_BACKWARD)
    def set(self, argv):
        (group, subgroup, task) = self._backward_parser(argv, require_prefix=True)

        prop_name = None
        if len(argv) > 0:
            prop_name = argv.pop(0)
            if len(argv) > 0:
                prop_value = argv.pop(0)
            else:
                prop_value = prompt("Value for property: %s" % prop_name)

        maybe_raise_unrecognized_argument(argv)

        if prop_name is None:
            prop = prompt("Name and Value for property").split('\n', 1)
            prop_name = prop.pop(0).strip()
            prop_value = prop.pop(0).strip() if len(prop) > 0 else ''

        data = self._load_task_data(group, subgroup, task)
        if prop_name and data_set_property(data, prop_name, prop_value):
            msg.normal("Set property of: %s" % _(group, subgroup, task))
            self._save_task(group, subgroup, task, data)
        else:
            msg.normal("Operation cancelled.")

    @command("e", [], SELECT_BACKWARD)
    def edit(self, argv):
        (group, subgroup, task) = self._backward_parser(argv)
        maybe_raise_unrecognized_argument(argv)

        data_pretty = json.dumps(self._load_task_data(group, subgroup, task),
                                 indent=4)
        selector = _(group, subgroup, task)
        new_data_raw = prompt("Editing: %s" % selector, data_pretty, "json")

        if new_data_raw:
            new_data = json.loads(new_data_raw)
            if is_valid_task_data(new_data):
                msg.normal("Manually edited: %s" % selector)
                self._save_task(group, subgroup, task, new_data)
            else:
                msg.error("Invalid data.")
        else:
            msg.normal("Operation cancelled.")

    @command()
    def rebuild_index(self, argv):
        maybe_raise_unrecognized_argument(argv)
        self.index.rebuild()
        self.index.save()

    # ===========================================
    # Main

    def interpret(self, argv):
        global HOOKS_ENABLED
        global CHECK_HOOKS
        directory = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                msg.turn_verbose_on()
            elif opt in ["--no-hooks"]:
                HOOKS_ENABLED = False
            elif opt in ["--check-hooks"]:
                CHECK_HOOKS = True
            elif opt in ["--directory", "-d"]:
                directory = argv.pop(0)
            elif opt in ["--help", "-h"]:
                msg.normal(__doc__)
                return
            else:
                raise ArgumentError("No such option: %s" % opt)

        self._setup_base_path(directory)

        if len(argv) == 0:
            raise ArgumentError("Missing command.")

        cmd = argv.pop(0)
        if cmd not in COMMAND_INFO:
            raise ArgumentError("No such command: %s" % cmd)

        readonly_cmd = COMMAND_INFO[cmd]["readonly"]
        cmd_name = COMMAND_INFO[cmd]['name']

        self._call_hook("before", cmd_name)
        if readonly_cmd:
            self._call_hook("before_read", cmd_name)
        else:
            self._call_hook("before_write", cmd_name)

        self._load_current()
        self._load_previous()
        self.index.load(self.base_path)
        getattr(self, cmd_name)(argv)

        if readonly_cmd:
            self._call_hook("after_read", cmd_name)
        else:
            self._call_hook("after_write", cmd_name)
        self._call_hook("after", cmd_name)

# ===========================================
# Entry Point


def interpret(argv):
    try:
        dit = Dit()
        dit.interpret(argv)
    except DitError as err:
        msg.error(err)
    except SubprocessError as err:
        msg.error("`%s` returned with non-zero code, aborting." % err)
    except IndexError as err:
        # this was probably caused by a pop on an empty argument list
        msg.error("Missing argument.")
    except json.decoder.JSONDecodeError:
        msg.error("Invalid JSON.")
    except re.error as err:
        # this was probably caused by a bad regex in the --where filter
        msg.error("Bad regular expression: %s" % err)
