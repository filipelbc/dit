#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usage: dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. Defaults to '~/.dit'.

  --verbose, -v
    Prints detailed information of what is being done.

  --help, -h
    Prints this message and quits.

  <command>:

    new <name> [-d "description"]
      Creates a new task.

    workon <id> | <name> | --new, -n <name> [-d "description"]
      Clocks in the specified task.
      --new, -n
        Same as 'new' followed by 'workon'.

    halt [<id> | <name>]
      Clocks out of the current task or the specified one.

    switchto <id> | <name> | --new, -n <name> [-d "description"]
      Same as 'halt' followed by 'workon'.

    conclude [<id> | <name>]
      Concludes the current task or the specified one. Note that there is a
      implicit 'halt'.

    status [<gid> | <gname>]
      Prints an overview of the situation for the specified group, subgroup,
      or task. Exports current task or subgroup unless something is specified.

    list
      This is a convenience alias for 'export', with "--output stdout".

    export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"] [<gid> | <gname>]
      Exports data to the specified format. Exports current subgroup unless
      something is specified.
      --concluded, -a
        Include concluded tasks in the listing.
      --all, -a
        Exports all groups and subgroups.
      --verbose, -v
        More information is printed.
      --output, -o
        File to which to export. Defaults to "stdout".
        Format is deduced from file extension if present.

  <name>: ["group-name"/]["subgroup-name"/]"task-name"
    "a"
        task "a" in current group/subgroup
    "b/a"
        task "a" in subgroup "b" in current group
    "c/b/a"
        task "a" in subgroup "b" in group "c"

    Note that "b" and "c" can be empty strings.

  <id>: --id, -i ["group-id"/]["subgroup-id"/]"task-id"
    "a"
        task "id a" in current subgroup in current group
    "b/a"
        task "id a" in subgroup "id b" in current group
    "c/b/a"
        task "id a" in subgroup "id b" in group "id c"

    Note that "b" and "c" can be empty strings, which map to "id 0".

  <gname>: "group-name"[/"subgroup-name"][/"task-name"]
    "a"
        group "a"
    "a/b"
        subgroup "b" in group "a"
    "a/b/c"
        task "c" in subgroup "b" in group "a"

    Note that "a" and "b" can be empty strings, which means the same as ".".

  <gid>: --id, -i "group-id"[/"subgroup-id"][/"task-id"]
    "a"
        group "id a"
    "a/b"
        subgroup "id b" in group "id a"
    "a/b/c"
        task "id c" in subgroup "id b" in group "id a"

    Note that "a" and "b" can be empty strings, which are mapped to "id 0".
"""

import sys
import json
import os

from importlib import import_module

from .data_utils import now

# ===========================================
# Custom Exceptions


class DitException(Exception):
    pass


class InvalidArgumentsError(DitException):
    pass

# ===========================================
# Dit Class


class Dit:
    directory = "~/.dit"
    current_fn = "CURRENT"
    index_fn = "INDEX"
    separator = "/"
    root_name = ""
    root_name_cmd = "."

    current_group = None
    current_subgroup = None
    current_task = None

    index = [[root_name, [[root_name, []]]]]

    printer = None

    # ===========================================
    # Paths and files names

    def _base_path(self):
        path = os.path.expanduser(os.path.join(self.directory))
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _current_path(self):
        return os.path.join(self._base_path(), self.current_fn)

    def _index_path(self):
        return os.path.join(self._base_path(), self.index_fn)

    def _subgroup_path(self, group, subgroup):
        path = os.path.join(self._base_path(), group, subgroup)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _task_path(self, group, subgroup, task):
        if not task:
            raise DitException("Invalid task")
        return os.path.join(self._subgroup_path(group, subgroup), task)

    # ===========================================
    # Checks

    def _is_current(self, group, subgroup, task):
        return (task == self.current_task and
                subgroup == self.current_subgroup and
                group == self.current_group)

    def _is_valid_name(self, name):
        return ((name == self.root_name) or
                (name[0].isalpha() and
                 name not in [self.current_fn, self.index_fn]))

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

    def _create_task(self, group, subgroup, task, description):
        fn = self._task_path(group, subgroup, task)
        if os.path.isfile(fn):
            raise DitException("Already exists: %s" % fn)
        if not description:
            description = input("Description: ")
        data = self._new_task_data(description)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))
        self._add_to_index(group, subgroup, task)
        self._save_index()

    def _load_task_data(self, group, subgroup, task):
        task_fp = self._task_path(group, subgroup, task)
        if not os.path.isfile(task_fp):
            raise DitException("Is not a file: %s" % task_fp)
        with open(task_fp, 'r') as f:
            return json.load(f)

    def _save_task(self, group, subgroup, task, data):
        fn = self._task_path(group, subgroup, task)
        data['updated_at'] = now()
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    # Current Task

    def _set_current(self, group, subgroup, task):
        self.current_group = group
        self.current_subgroup = subgroup
        self.current_task = task

    def _save_current(self):
        current = {
            'group': self.current_group,
            'subgroup': self.current_subgroup,
            'task': self.current_task
        }
        current_fp = self._current_path()
        with open(current_fp, 'w') as f:
            json.dump(current, f)

    def _load_current(self):
        current_fp = self._current_path()
        if os.path.isfile(current_fp):
            with open(current_fp, 'r') as f:
                current = json.load(f)
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
            self.index.append([group, [[self.root_name, []]]])

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
        index_fp = self._index_path()
        with open(index_fp, 'w') as f:
            json.dump(self.index, f)

    def _load_index(self):
        index_fp = self._index_path()
        if os.path.isfile(index_fp):
            with open(index_fp, 'r') as f:
                self.index = json.load(f)

    def _rebuild_index(self):
        self.index = [[self.root_name, [[self.root_name, []]]]]
        c_group = None
        c_subgroup = None
        base_path = self._base_path()
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if not self._is_valid_name(f):
                    continue
                p = root[len(base_path) + 1:].split("/")
                p = [i for i in p if i]
                if len(p) == 0:
                    group, subgroup = self.root_name, self.root_name
                elif len(p) == 1:
                    group, subgroup = self.root_name, p[0]
                elif len(p) == 2:
                    group, subgroup = p
                else:
                    continue

                if group != c_group:
                    c_group = group
                    self.index.append([group, [[self.root_name, []]]])

                if subgroup != c_subgroup:
                    c_subgroup = subgroup
                    self.index[-1][1].append([subgroup, []])

                self.index[-1][1][-1][1].append(f)

        self._save_index()

    # ===========================================
    # Export

    def _export_task_(self, group, group_id, subgroup, subgroup_id, task, task_id):
        data = self._load_task_data(group, subgroup, task)
        self.printer.task(group, group_id, subgroup, subgroup_id, task, task_id, data)

    def _export_task(self, group, subgroup, task):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                for j in range(len(self.index[i][1])):
                    if self.index[i][1][j][0] == subgroup:
                        for k in range(len(self.index[i][1][j][1])):
                            if self.index[i][1][j][1][k] == task:
                                self._export_task_(group,     i,
                                                   subgroup,  j,
                                                   task,      k)

    def _export_tasks(self, group_id, subgroup_id):
        n_tasks = len(self.index[group_id][1][subgroup_id][1])

        if n_tasks > 0:
            group = self.index[group_id][0]
            subgroup = self.index[group_id][1][subgroup_id][0]

            self.printer.subgroup(group, group_id, subgroup, subgroup_id)

            for i in range(n_tasks):
                task = self.index[group_id][1][subgroup_id][1][i]
                self._export_task_(group,    group_id,
                                   subgroup, subgroup_id,
                                   task,     i)

    def _export_subgroup(self, group, subgroup):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                self.printer.group(group, i)
                for j in range(len(self.index[i][1])):
                    if self.index[i][1][j][0] == subgroup:
                        self._export_tasks(i, j)

    def _export_group(self, group):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                self.printer.group(group, i)
                for j in range(len(self.index[i][1])):
                    self._export_tasks(i, j)

    def _export_all(self):
        for i in range(len(self.index)):
            self.printer.group(self.index[i][0], i)
            for j in range(len(self.index[i][1])):
                self._export_tasks(i, j)

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

    def _gid_parse(self, argv):
        ids = argv.pop(0).split(self.separator)
        if len(ids) > 3:
            raise DitException("Invalid gID format")
        ids = [int(i) if i else "0" for i in ids]
        ids = ids + [None] * (3 - len(ids))
        group_id, subgroup_id, task_id = ids

        group = self.index[group_id][0]

        subgroup = None
        task = None

        if subgroup_id:
            subgroup = self.index[group_id][1][subgroup_id][0]
            if task_id:
                task = self.index[group_id][1][subgroup_id][1][task_id]

        return (group, subgroup, task)

    def _id_parse(self, argv):
        ids = argv.pop(0).split(self.separator)
        if len(ids) > 3:
            raise DitException("Invalid ID format")
        ids = [int(i) if i else "0" for i in ids]
        ids = [None] * (3 - len(ids)) + ids
        group_id, subgroup_id, task_id = ids

        if group_id is None:
            for i in range(len(self.index)):
                if self.index[i][0] == self.current_group:
                    group_id = i
                    break

        if subgroup_id is None:
            for i in range(len(self.index[group_id][1])):
                if self.index[group_id][1][i][0] == self.current_subgroup:
                    subgroup_id = i
                    break

        group = self.index[group_id][0]
        subgroup = self.index[group_id][1][subgroup_id][0]
        task = self.index[group_id][1][subgroup_id][1][task_id]

        return (group, subgroup, task)

    def _gname_parse(self, argv):
        names = argv.pop(0).split(self.separator)
        if len(names) > 3:
            raise DitException("Invalid gname format")
        names = [name if name != self.root_name_cmd else self.root_name for name in names]
        names = names + [None] * (3 - len(names))
        group, subgroup, task = names

        for name in [group, subgroup, task]:
            if name and not self._is_valid_name(name):
                raise DitException("Invalid name: %s" % name)

        return (group, subgroup, task)

    def _name_parse(self, argv):
        names = argv.pop(0).split(self.separator)
        if len(names) > 3:
            raise DitException("Invalid name format")
        names = [name if name != self.root_name_cmd else self.root_name for name in names]
        names = [None] * (3 - len(names)) + names

        group, subgroup, task = names

        if group is None:
            if self.current_group is not None:
                group = self.current_group
            else:
                group = self.root_name

        if subgroup is None:
            if self.current_subgroup is not None:
                subgroup = self.current_subgroup
            else:
                subgroup = self.root_name

        for name in [group, subgroup, task]:
            if not self._is_valid_name(name):
                raise DitException("Invalid name: %s" % name)

        return (group, subgroup, task)

    # ===========================================
    # Commands

    def usage():
        print(__doc__)

    def new(self, argv):
        if len(argv) < 1:
            raise InvalidArgumentsError("Missing argument")

        (group, subgroup, task) = self._name_parse(argv)

        description = None
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--description", "-d"]:
                description = argv.pop(0)
            else:
                raise InvalidArgumentsError("No such option: %s" % opt)
        if not description:
            description = input("Description: ")

        self._create_task(group, subgroup, task, description)

        return (group, subgroup, task)

    def workon(self, argv):
        if len(argv) < 1:
            raise InvalidArgumentsError("Missing argument")

        group = self.current_group
        subgroup = self.current_subgroup
        task = self.current_task

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--new", "-n"]:
                (group, subgroup, task) = self.new(argv)
            elif opt in ["--id", '-i']:
                (group, subgroup, task) = self._id_parse(argv)
            else:
                raise InvalidArgumentsError("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._name_parse(argv)

        if task:
            data = self._load_task_data(group, subgroup, task)

            self._clock_in(data)
            self._save_task(group, subgroup, task, data)
            self._set_current(group, subgroup, task)
            self._save_current()
        else:
            raise InvalidArgumentsError("No task specified")

    def halt(self, argv, also_conclude=False):
        group = self.current_group
        subgroup = self.current_subgroup
        task = self.current_task

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--id", '-i']:
                (group, subgroup, task) = self._id_parse(argv)
            else:
                raise InvalidArgumentsError("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._name_parse(argv)

        if not task:
            if also_conclude:
                raise InvalidArgumentsError("No task specified")
            else:
                print("Not working on any task")
            return

        data = self._load_task_data(group, subgroup, task)

        self._clock_out(data)
        if also_conclude:
            self._conclude(data)
        self._save_task(group, subgroup, task, data)

        if self._is_current(group, subgroup, task):
            self.current_task = None
            self._save_current()

    def switchto(self, argv):
        self.halt()
        self.workon(argv)

    def conclude(self, argv):
        self.halt(argv, also_conclude=True)

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
            elif opt in ["--id", '-i']:
                (group, subgroup, task) = self._gid_parse(argv)
            else:
                raise InvalidArgumentsError("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._gname_parse(argv)

        if statussing and group is None:
            group = self.current_group
            subgroup = self.current_subgroup
            task = self.current_task

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
            print("Nothing to do")

        self.printer.end()

        file.close()

    # ===========================================
    # Main

    def configure(self, argv):
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                self.verbose = True
            elif opt in ["--directory", "-d"]:
                self.directory = argv.pop(0)
            elif opt in ["--help", "-h"]:
                self.usage()
                return False
            else:
                raise InvalidArgumentsError("No such option: %s" % opt)
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
            else:
                raise InvalidArgumentsError("No such command: %s" % cmd)
        else:
            raise InvalidArgumentsError("Missing command")

# ===========================================
# Main


def main():
    argv = sys.argv
    argv.pop(0)

    try:
        dit = Dit()
        if dit.configure(argv):
            dit.interpret(argv)
    except DitException as err:
        print("Error: %s" % err)
        print("Type 'dit --help' for usage details.")

if __name__ == "__main__":
    main()
