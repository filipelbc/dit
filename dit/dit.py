#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage: dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. Defaults to '~/.dit'.

  --verbose, -v
    Prints detailed information of what is being done.

  --rebuild-index
    Rebuild the INDEX file. For use in case of manual modification of the
    contents of "--directory".

  --help, -h
    Prints this message and quits.

  <command>:

    new <name> [-: "description"]
      Creates a new task. You will be prompted for the "descroption" if it is
      not provided.

    workon <id> | <name> | --new, -n <name> [-: "description"]
      Clocks in the specified task.
      --new, -n
        Same as 'new' followed by 'workon'.

    halt [<id> | <name>]
      Clocks out of the current task or the specified one.

    switchto <id> | <name> | --new, -n <name> [-: "description"]
      Same as 'halt' followed by 'workon'.

    conclude [<id> | <name>]
      Concludes the current task or the selected one. Note that there is a
      implicit 'halt'.

    status [<gid> | <gname>]
      Prints an overview of the data for the current task or subgroup, or
      for the selected one.

    list
      This is a convenience alias for 'export', with "--output stdout".

    export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"] [<gid> | <gname>]
      Prints most of the data for the current subgroup or the selected one.
      --concluded, -a
        Include concluded tasks.
      --all, -a
        Select all groups and subgroups.
      --verbose, -v
        All information is exported.
      --output, -o
        File to which to write. Defaults to "stdout". Format is deduced from
        file extension if present.

    note [<name> | <id>] [-: "text"]
      Adds a note to the current task or the specified one.

    set [<name> | <id>] [-: "name" ["value"]]
      Sets a property for the current task or the specified one. The format
      of properties are pairs of strings (name, value).

    edit [<name> | <id>]
      Opens the specified task for manual editing. Uses current task if none is
      specified. If $EDITOR environment variable is not set it does nothing.

  "-:"
    Arguments preceeded by "-:" are necessary. If omited, then: a) if the
    $EDITOR environment variable is set, a text file will be open for
    editing the argument; b) otherwise, a simple prompt will be used.

  <name>: ["group-name"/]["subgroup-name"/]"task-name"
    "a"
        task "a" in current group/subgroup
    "b/a"
        task "a" in subgroup "b" in current group
    "c/b/a"
        task "a" in subgroup "b" in group "c"

    A name must begin with a letter to be valid. "b" and "c" can be empty
    or a dot, which means no subgroup and group repectively.

  <id>: ["group-id"/]["subgroup-id"/]"task-id"
    "a"
        task "id a" in current subgroup in current group
    "b/a"
        task "id a" in subgroup "id b" in current group
    "c/b/a"
        task "id a" in subgroup "id b" in group "id c"

  <gname>: "group-name"[/"subgroup-name"][/"task-name"]
    "a"
        group "a"
    "a/b"
        subgroup "b" in group "a"
    "a/b/c"
        task "c" in subgroup "b" in group "a"

    A name must begin with a letter to be valid. "a" and "b" can be empty
    or a dot, which means no subgroup and group repectively.

  <gid>: "group-id"[/"subgroup-id"][/"task-id"]
    "a"
        group "id a"
    "a/b"
        subgroup "id b" in group "id a"
    "a/b/c"
        task "id c" in subgroup "id b" in group "id a"
"""

import sys
import json
import os
import subprocess

from importlib import import_module

from .utils import make_tmp_fp
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
# Dit Class


class Dit:
    CURRENT_FN = "CURRENT"
    INDEX_FN = "INDEX"
    SEPARATOR = "/"
    COMMENT_CHAR = "#"
    ROOT_NAME = ""
    ROOT_NAME_VERB = "."
    DEFAULT_DIR = "~/.dit"

    current_group = None
    current_subgroup = None
    current_task = None

    index = [[ROOT_NAME, [[ROOT_NAME, []]]]]

    base_path = None
    printer = None
    verbose = False

    # ===========================================
    # Trace and Verbosity

    # helpers

    def _printable(self, name, *others):

        def _(n):
            if n is None:
                return "_"
            return self.ROOT_NAME_VERB if n == self.ROOT_NAME else n

        ret = _(name)
        for other in others:
            ret += self.SEPARATOR + _(other)

        return ret

    def print_verb(self, message):
        if self.verbose:
            print(message)

    def print_selected(self, group, subgroup, task):
        self.print_verb("Selected: %s" % self._printable(group, subgroup, task))

    # ===========================================
    # Paths and files names

    def _setup_base_path(self, directory):
        path = os.path.expanduser(directory)
        if not os.path.exists(path):
            os.makedirs(path)
            self.print_verb("Created path: %s" % path)
        self.base_path = path

    def _current_path(self):
        return os.path.join(self.base_path, self.CURRENT_FN)

    def _index_path(self):
        return os.path.join(self.base_path, self.INDEX_FN)

    def _get_task_path(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup, task)
        if not os.path.isfile(path):
            raise DitException("No such task file: %s" % path)
        return path

    def _make_task_path(self, group, subgroup, task):
        path = os.path.join(self.base_path, group, subgroup)
        if not os.path.exists(path):
            os.makedirs(path)
            self.print_verb("Created path: %s" % path)
        return os.path.join(path, task)

    # ===========================================
    # Checks

    def _is_current(self, group, subgroup, task):
        return (task == self.current_task and
                subgroup == self.current_subgroup and
                group == self.current_group)

    def _is_valid_group_name(self, name):
        return ((name == self.ROOT_NAME) or
                (len(name) > 0 and
                 name[0].isalpha() and
                 name not in [self.CURRENT_FN, self.INDEX_FN]))

    def _is_valid_task_name(self, name):
        return (len(name) > 0 and
                name[0].isalpha() and
                name not in [self.CURRENT_FN, self.INDEX_FN])

    # ===========================================
    # I/O

    @staticmethod
    def _load_json_file(fp):
        if os.path.isfile(fp):
            with open(fp, 'r') as f:
                return json.load(f)
        return None

    @staticmethod
    def _save_json_file(fp, data):
        with open(fp, 'w') as f:
            f.write(json.dumps(data))

    # ===========================================
    # Task management

    @staticmethod
    def _new_task_data(description=None):
        return {
            "description": description,
            "logbook": [],
            "properties": [],
            "notes": [],
            "created_at": now()
        }

    @staticmethod
    def _is_valid_task_data(data):
        return isinstance(data, dict)

    def _create_task(self, group, subgroup, task, description):
        task_fp = self._make_task_path(group, subgroup, task)
        if os.path.isfile(task_fp):
            raise DitException("Task file already exists: %s" % task_fp)
        data = self._new_task_data(description)
        self._save_json_file(task_fp, data)
        self._add_to_index(group, subgroup, task)
        self._save_index()

    def _load_task_data(self, group, subgroup, task):
        task_fp = self._get_task_path(group, subgroup, task)
        task = self._load_json_file(task_fp)
        if not self._is_valid_task_data(task):
            raise DitException("Task file contains invalid data: %s" % task_fp)
        return task

    def _save_task(self, group, subgroup, task, data):
        task_fp = self._make_task_path(group, subgroup, task)
        data['updated_at'] = now()
        self._save_json_file(task_fp, data)
        self.print_verb("Task saved: %s" % self._printable(group, subgroup, task))

    @staticmethod
    def _add_note(data, note_text):
        if 'notes' not in data:
            data['notes'] = []
        data['notes'].append(note_text)

    @staticmethod
    def _set_property(data, prop_name, prop_value):
        if 'properties' not in data:
            data['properties'] = []

        properties = data['properties']
        for prop in properties:
            if prop_name == prop['name']:
                prop['value'] = prop_value
                return
        properties.append({'name': prop_name, 'value': prop_value})

    # Current Task

    def _set_current(self, group, subgroup, task):
        self.current_group = group
        self.current_subgroup = subgroup
        self.current_task = task

    def _save_current(self):
        current_data = {
            'group': self.current_group,
            'subgroup': self.current_subgroup,
            'task': self.current_task
        }
        self._save_json_file(self._current_path(), current_data)
        self.print_verb("Current task saved.")

    def _load_current(self):
        current = self._load_json_file(self._current_path())
        if current is not None:
            self._set_current(current['group'],
                              current['subgroup'],
                              current['task'])

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
            self.index.append([group, [[self.ROOT_NAME, []]]])

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
        self._save_json_file(self._index_path(), self.index)
        self.print_verb("Index saved.")

    def _load_index(self):
        index_fp = self._index_path()
        index = self._load_json_file(index_fp)
        if index is not None:
            self.index = index

    def _rebuild_index(self):
        self.index = [[self.ROOT_NAME, [[self.ROOT_NAME, []]]]]
        c_group = self.ROOT_NAME
        c_subgroup = self.ROOT_NAME
        for root, dirs, files in os.walk(self.base_path):
            dirs.sort()
            for f in sorted(files):
                if not self._is_valid_task_name(f):
                    continue
                p = root[len(self.base_path) + 1:].split(os.sep)

                p = [i for i in p if i]
                if len(p) == 0:
                    group, subgroup = self.ROOT_NAME, self.ROOT_NAME
                elif len(p) == 1:
                    group, subgroup = p[0], self.ROOT_NAME
                elif len(p) == 2:
                    group, subgroup = p
                else:
                    continue

                if group != c_group:
                    c_group = group
                    c_subgroup = self.ROOT_NAME
                    self.index.append([group, [[self.ROOT_NAME, []]]])

                if subgroup != c_subgroup:
                    c_subgroup = subgroup
                    self.index[-1][1].append([subgroup, []])

                self.index[-1][1][-1][1].append(f)

        self.print_verb("Index rebuilt.")

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
    # Clock

    def _clock_in(self, data):
        logbook = data.get('logbook', [])
        if len(logbook) > 0:
            last = logbook[-1]
            if not last['out']:
                print("Already clocked in")
                return
        data['logbook'] = logbook + [{'in': now(), 'out': None}]

    def _clock_out(self, data):
        logbook = data.get('logbook', [])
        if len(logbook) == 0:
            print("Already clocked out")
            return
        last = logbook[-1]
        if last['out']:
            print("Already clocked out")
            return
        last['out'] = now()
        data['logbook'] = logbook

    def _conclude(self, data):
        if data.get('concluded_at', None):
            print("Already concluded")
            return
        data['concluded_at'] = now()

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
            raise DitException("Invalid index format, must be an integer: %s" % idx)
        except IndexError:
            raise DitException("Invalid index: %d" % idx)

        return names

    def _gid_parser(self, argv):
        idxs = argv.pop(0).split(self.SEPARATOR)
        if len(idxs) > 3:
            raise DitException("Invalid <gid> format.")

        # replaces missing subgroup or task with None
        idxs = idxs + [None] * (3 - len(idxs))

        return self._idxs_to_names(idxs, self.index)

    def _id_parser(self, argv):
        idxs = argv.pop(0).split(self.SEPARATOR)
        if len(idxs) > 3:
            raise DitException("Invalid <id> format.")

        # replaces missing group or subgroup with current
        group_idx, subgroup_idx = self._current_idxs()
        if len(idxs) == 1:
            idxs = [group_idx, subgroup_idx] + idxs
        elif len(idxs) == 2:
            idxs = [group_idx] + idxs

        return self._idxs_to_names(idxs, self.index)

    def _gname_parser(self, argv):
        names = argv.pop(0).split(self.SEPARATOR)
        if len(names) > 3:
            raise DitException("Invalid <gname> format.")
        names = [name if name != self.ROOT_NAME_VERB else self.ROOT_NAME for name in names]
        names = names + [None] * (3 - len(names))
        group, subgroup, task = names

        for name in [group, subgroup]:
            if name and not self._is_valid_group_name(name):
                raise DitException("Invalid group name: %s" % name)
        if task and not self._is_valid_task_name(task):
            raise DitException("Invalid task name: %s" % task)

        if group == self.ROOT_NAME and subgroup:
            group, subgroup = subgroup, (self.ROOT_NAME if task else None)

        return (group, subgroup, task)

    def _name_parser(self, argv):
        names = argv.pop(0).split(self.SEPARATOR)
        if len(names) > 3:
            raise DitException("Invalid <name> format.")
        names = [name if name != self.ROOT_NAME_VERB else self.ROOT_NAME for name in names]
        names = [None] * (3 - len(names)) + names

        group, subgroup, task = names

        if group is None:
            if self.current_group is not None:
                group = self.current_group
            else:
                group = self.ROOT_NAME

        if subgroup is None:
            if self.current_subgroup is not None:
                subgroup = self.current_subgroup
            else:
                subgroup = self.ROOT_NAME

        for name in [group, subgroup]:
            if not self._is_valid_group_name(name):
                raise DitException("Invalid group name: %s" % name)
        if not self._is_valid_task_name(task):
            raise DitException("Invalid task name: %s" % task)

        if group == self.ROOT_NAME and subgroup:
            group, subgroup = subgroup, group

        return (group, subgroup, task)

    def _backward_parser(self, argv):
        group = self.current_group
        subgroup = self.current_subgroup
        task = self.current_task
        if len(argv) > 0:
            if argv[0][0].isdigit():
                (group, subgroup, task) = self._id_parser(argv)
            elif not argv[0].startswith("-"):
                (group, subgroup, task) = self._name_parser(argv)

        self.print_selected(group, subgroup, task)

        if not task:
            raise NoTaskSpecifiedCondition("No task specified.")

        return (group, subgroup, task)

    def _forward_parser(self, argv):
        if argv[0][0].isdigit():
            return self._gid_parser(argv)
        elif not argv[0].startswith("-"):
            return self._gname_parser(argv)

    # ===========================================
    # Input

    def _prompt(self, header, initial=None, extension='txt'):
        editor = os.environ.get('EDITOR', None)
        if editor:
            input_fp = make_tmp_fp(header, extension)
            with open(input_fp, 'w') as f:
                f.write(self.COMMENT_CHAR + ' ' + header + '\n')
                if initial:
                    f.write(initial)
            subprocess.run([editor, input_fp])
            with open(input_fp, 'r') as f:
                lines = [line for line in f.readlines() if not line.startswith(self.COMMENT_CHAR)]
            return (''.join(lines)).strip()

        elif not initial:
            return input(header + ': ').strip()

        else:
            raise DitException("$EDITOR environment variable is not set.")

    # ===========================================
    # Commands

    def usage(self):
        print(__doc__)

    def new(self, argv):
        if len(argv) < 1:
            raise ArgumentException("Missing argument.")

        (group, subgroup, task) = self._name_parser(argv)
        self.print_selected(group, subgroup, task)

        description = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            description = argv.pop(0)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if description is None:
            description = self._prompt('Description')

        self._create_task(group, subgroup, task, description)

        return (group, subgroup, task)

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

        data = self._load_task_data(group, subgroup, task)
        self._clock_in(data)
        self._save_task(group, subgroup, task, data)
        self._set_current(group, subgroup, task)
        self._save_current()

    def halt(self, argv, conclude=False):
        try:
            (group, subgroup, task) = self._backward_parser(argv)
        except NoTaskSpecifiedCondition as ex:
            self.print_verb('Not working on any task.')
            return

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        data = self._load_task_data(group, subgroup, task)

        self._clock_out(data)
        if conclude:
            self._conclude(data)
        self._save_task(group, subgroup, task, data)

        if self._is_current(group, subgroup, task):
            self.current_task = None
            self._save_current()

    def switchto(self, argv):
        self.halt([])
        self.workon(argv)

    def conclude(self, argv):
        self.halt(argv, conclude=True)

    def status(self, argv):
        self.export(argv, statussing=True)

    def list(self, argv):
        self.export(argv, listing=True)

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
            group = self.current_group
            subgroup = self.current_subgroup
            task = self.current_task

        self.print_selected(group, subgroup, task)

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

    def note(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        note_text = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            note_text = argv.pop(0)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if note_text is None:
            note_text = self._prompt("Description")

        data = self._load_task_data(group, subgroup, task)
        self._add_note(data, note_text)
        self._save_task(group, subgroup, task, data)

    def set(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        prop_name = None
        if len(argv) > 0 and argv[0] in ["-:", "--:"]:
            argv.pop(0)
            prop_name = argv.pop(0)
            if len(argv) > 0:
                prop_value = argv.pop(0)
            else:
                prop_value = self._prompt("Value for '%s'" % prop_name)

        if len(argv) > 0:
            raise ArgumentException("Unrecognized argument: %s" % argv[0])

        if prop_name is None:
            prop = self._prompt("Name and Value for property").split('\n', 1)
            prop_name = prop[0].strip()
            if len(prop) == 2:
                prop_value = prop[1].strip()
            else:
                prop_value = ''

        data = self._load_task_data(group, subgroup, task)
        self._set_property(data, prop_name, prop_value)
        self._save_task(group, subgroup, task, data)

    def edit(self, argv):
        group, subgroup, task = self._backward_parser(argv)

        data_pretty = json.dumps(self._load_task_data(group, subgroup, task),
                                 indent=4)
        header = "Editing: " + self._printable(group, subgroup, task)

        new_data_raw = self._prompt(header, data_pretty, "json")

        if new_data_raw:
            new_data = json.loads(new_data_raw)
            if self._is_valid_task_data(new_data):
                self._save_task(group, subgroup, task, new_data)
            else:
                print("Invalid data type, should be a dictionary.")
        else:
            print("Operation cancelled.")

    # ===========================================
    # Main

    def configure(self, argv):
        rebuild_index = False
        directory = self.DEFAULT_DIR

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                self.verbose = True
            elif opt in ["--directory", "-d"]:
                directory = argv.pop(0)
            elif opt in ["--rebuild-index", '-r']:
                rebuild_index = True
            elif opt in ["--help", "-h"]:
                self.usage()
                return False
            else:
                raise ArgumentException("No such option: %s" % opt)

        self._setup_base_path(directory)
        if rebuild_index:
            self._rebuild_index()
            self._save_index()
        self._load_current()
        self._load_index()
        return True

    def interpret(self, argv):
        if len(argv) > 0:
            cmd = argv.pop(0)
            if cmd in ["new", "n"]:
                self.new(argv)
            elif cmd in ["workon", "w"]:
                self.workon(argv)
            elif cmd in ["switchto", "s"]:
                self.switchto(argv)
            elif cmd in ["halt", "h"]:
                self.halt(argv)
            elif cmd in ["conclude", "c"]:
                self.conclude(argv)
            elif cmd in ["status", "q"]:
                self.status(argv)
            elif cmd in ["list", "l"]:
                self.list(argv)
            elif cmd in ["export", "e"]:
                self.export(argv)
            elif cmd in ["note", "t"]:
                self.note(argv)
            elif cmd in ["set", "p"]:
                self.set(argv)
            elif cmd in ["edit", "m"]:
                self.edit(argv)
            else:
                raise ArgumentException("No such command: %s" % cmd)
        else:
            raise ArgumentException("Missing command.")

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
        print("ERROR: %s" % err)
        print("Type 'dit --help' for usage details.")
    except IndexError as err:
        # this was probably caused by a pop on an empty argument list
        print("ERROR: Missing argument.")
        print("Type 'dit --help' for usage details.")
    except json.decoder.JSONDecodeError:
        print("ERROR: Invalid JSON.")

if __name__ == "__main__":
    main()
