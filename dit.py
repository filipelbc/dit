#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:        Filipe L B Correia <filipelbc@gmail.com>
# Contributor:   Daniel Moraes <daniel.b.moraes@gmail.com>
#
# About:         Command line work time tracking and todo list
#
# =============================================================================

"""
Usage:

  dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. Defaults to '~/.dit'.

  --verbose, -v
    Prints detailed information of what is done.

  --help, -h
    Prints this message and quits.

  <command>:

    new <name> [-d "description"]
      Creates a new task.

    workon <id> | --new, -n <name> [-d "description"]
      Clocks in the specified task.
      --new, -n
        Same as 'new' followed by 'workon'.

    halt [<id> | <name>]
      Clocks out of the specified task or the current one.

    switchto <id> | --new, -n <name> [-d "description"]
      Same as 'halt' followed by 'workon'

    conclude [<id> | <name>]
      Concludes the specified task or the current one. Note that there is an
      implicit 'halt'

    status [<gid> | <gname>]
      Prints an overview of the situation for the specified group, subgroup,
      or task. If none specified, the current task is used.

    list
      This is a convenience alias for 'export'

    export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"]
        [<gid> | <gname>]
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

  <id>: --id, -i ["group-id"/]["subgroup-id"/]"task-id"

      Uses current group and current subgroup if they are not specified.

  <gname>: "group-name"[/"subgroup-name"][/"task-name"]

  <gid>: --id, -i "group-id"[/"subgroup-id"][/"task-id"]
"""

import sys
import json
import os

from datetime import datetime

# ==============
# Options


class Dit:
    directory = "~/dit"
    current_fn = "CURRENT"
    index_fn = "INDEX"
    separator = "/"

    current_group = None
    current_subgroup = None
    current_task = None

    index = [[None, [[None, []]]]]

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
        if not group:
            group = ""
        if not subgroup:
            subgroup = ""
        path = os.path.join(self._base_path(), group, subgroup)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _task_path(self, group, subgroup, task):
        if not task:
            raise Exception("Invalid task")
        return os.path.join(self._subgroup_path(group, subgroup), task)

    # ===========================================
    # Auxiliary

    @staticmethod
    def _now():
        return str(datetime.now())

    @staticmethod
    def _is_valid_name(name):
        if name is not None:
            prohibited_names = ["CURRENT", "INDEX"]
            if name in prohibited_names:
                return False
            if not name[0].isalpha():
                return False
        return True

    @staticmethod
    def _new_task(description=None):
        return {
            "description": description,
            "logbook": [],
            "properties": [],
            "notes": [],
            "created_at": Dit._now()
        }

    def _create_task(self, group, subgroup, task, description):
        fn = self._task_path(group, subgroup, task)

        if os.path.isfile(fn):
            raise Exception("Already exists: %s" % fn)

        if not description:
            description = input("Description: ")

        data = self._new_task(description)

        with open(fn, 'w') as f:
            f.write(json.dumps(data))

        self._add_to_index(group, subgroup, task)
        self._save_index()

    @staticmethod
    def _get_task_data_fp(fp):
        if not os.path.isfile(fp):
            raise Exception("Is not a file: %s" % fp)

        with open(fp, 'r') as f:
            return json.load(f)

    def _get_task_data(self, group, subgroup, task):
        fp = self._task_path(group, subgroup, task)

        return self._get_task_data_fp(fp)

    def _save_task(self, group, subgroup, task, data):
        fn = self._task_path(group, subgroup, task)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

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
            self.index.append([group, [[None, []]]])

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
        self.index = [[None, [[None, []]]]]
        c_group = None
        c_subgroup = None
        for root, dirs, files in os.walk(self._base_path()):
            for f in files:
                if not self._is_valid_name(f):
                    continue
                p = root[len(self._base_path()) + 1:].split("/")
                p = [i for i in p if i]
                if len(p) == 0:
                    group, subgroup = None, None
                elif len(p) == 1:
                    group, subgroup = None, p[0]
                else:
                    group, subgroup = p

                if group != c_group:
                    c_group = group
                    self.index.append([group, [[None, []]]])

                if subgroup != c_subgroup:
                    c_subgroup = subgroup
                    self.index[-1][1].append([subgroup, []])

                self.index[-1][1][-1][1].append(f)

        self._save_index()

    # ===========================================
    # Export

    def _export_task_(self, group, subgroup, task, task_id, concluded, verbose):
        data = self._get_task_data(group, subgroup, task)

        if not data.get('concluded_at', None) or concluded:
            self.printer.task(group, subgroup, task, task_id, data, verbose)

    def _export_task(self, group, subgroup, task, concluded, verbose):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                for j in range(len(self.index[i][1])):
                    if self.index[i][1][j][0] == subgroup:
                        for k in range(self.index[i][1][j][1]):
                            if self.index[i][1][j][1][k] == task:
                                self._export_task_(group,     i,
                                                   subgroup,  j,
                                                   task,      k,
                                                   concluded, verbose)

    def _export_tasks(self, group_id, subgroup_id, concluded, verbose):
        n_tasks = len(self.index[group_id][1][subgroup_id][1])

        if n_tasks > 0:
            group = self.index[group_id][0]
            subgroup = self.index[group_id][1][subgroup_id][0]

            self.printer.subgroup(group, group_id, subgroup, subgroup_id, verbose)

            for i in range(n_tasks):
                task = self.index[group_id][1][subgroup_id][1][i]
                self._export_task_(group,    group_id,
                                   subgroup, subgroup_id,
                                   task,     i,
                                   concluded, verbose)

    def _export_subgroup(self, group, subgroup, concluded, verbose):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                self.printer.group(group, i)
                for j in range(len(self.index[i][1])):
                    if self.index[i][1][j][0] == subgroup:
                        self._export_tasks(i, j, concluded, verbose)

    def _export_group(self, group, concluded, verbose):
        for i in range(len(self.index)):
            if self.index[i][0] == group:
                self.printer.group(group, i)
                for j in range(len(self.index[i][1])):
                    self._export_tasks(i, j, concluded, verbose)

    def _export_all(self, concluded, verbose):
        for i in range(len(self.index)):
            self.printer.group(self.index[i][0], i)
            for j in range(len(self.index[i][1])):
                self._export_tasks(i, j, concluded, verbose)

    # ===========================================
    # Checks

    def _is_current(self, group, subgroup, task):
        if task != self.current_task \
                or subgroup != self.current_subgroup \
                or group != self.current_group:
            return False
        return True

    # ===========================================
    # Clock

    def _clock_in(self, data):
        if data['logbook']:
            last = data['logbook'][-1]
            if not last['out']:
                print("Already clocked in")
                return

        data['logbook'] += [{'in': self._now(), 'out': None}]

    def _clock_out(self, data):
        if not data['logbook']:
            print("Already clocked out")
            return
        last = data['logbook'][-1]
        if last['out']:
            print("Already clocked out")
            return

        last['out'] = self._now()

    def _conclude(self, data):
        if data.get('concluded_at', None):
            print("Already concluded")
            return
        data['concluded_at'] = self._now()

    # ===========================================
    # Parsers

    def _gid_parse(self, argv):
        ids = list(map(int, argv.pop(0).split(self.separator)))
        if len(ids) > 3:
            raise Exception("Invalid GID format")
        ids = ids + [None] * (3 - len(ids))
        group_id, subgroup_id, task_id = ids

        group = self.index[group_id][0]

        subgroup, task = None, None

        if subgroup_id:
            subgroup = self.index[group_id][1][subgroup_id][0]

        if task_id:
            task = self.index[group_id][1][subgroup_id][1][task_id]

        return (group, subgroup, task)

    def _id_parse(self, argv):
        ids = list(map(int, argv.pop(0).split(self.separator)))
        if len(ids) > 3:
            raise Exception("Invalid GID format")
        ids = [None] * (3 - len(ids)) + ids
        group_id, subgroup_id, task_id = ids

        if group_id:
            group = self.index[group_id][0]
        else:
            group = self.current_group
            for i in range(len(self.index)):
                if self.index[i][0] == group:
                    group_id = i
                    break

        if subgroup_id:
            subgroup = self.index[group_id][1][subgroup_id][0]
        else:
            subgroup = self.current_subgroup
            for i in range(len(self.index[group_id][1])):
                if self.index[group_id][1][i][0] == subgroup:
                    subgroup_id = i
                    break

        task = self.index[group_id][1][subgroup_id][1][task_id]

        return (group, subgroup, task)

    def _gname_parse(self, argv):
        names = argv.pop(0).split(self.separator)
        names = names + [None] * (3 - len(names))
        group, subgroup, task = names

        for name in [group, subgroup, task]:
            if not self._is_valid_name(name):
                raise Exception("Invalid name %s" % name)

        return (group, subgroup, task)

    def _name_parse(self, argv):
        names = argv.pop(0).split(self.separator)
        names = [None] * (3 - len(names)) + names
        group, subgroup, task = names

        for name in [group, subgroup, task]:
            if not self._is_valid_name(name):
                raise Exception("Invalid name %s" % name)

        return (group, subgroup, task)

    def _new_parse(self, argv):
        (group, subgroup, task) = self._name_parse(argv)

        description = None
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--description", "-d"]:
                description = argv.pop(0)
            else:
                raise Exception("No such option: %s" % opt)
        if not description:
            description = input("Description: ")

        return (group, subgroup, task, description)

    # ===========================================
    # Commands

    def new(self, argv):
        if len(argv) < 1:
            raise Exception("Missing argument")

        (group, subgroup, task, description) = self._new_parse(argv)

        self._create_task(group, subgroup, task, description)

        return (group, subgroup, task)

    def workon(self, argv):
        if len(argv) < 1:
            raise Exception("Missing argument")

        group = self.current_group
        subgroup = self.current_subgroup
        task = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--new", "-n"]:
                (group, subgroup, task) = self.new(argv)
            elif opt in ["--id", '-i']:
                (group, subgroup, task) = self._id_parse(argv)
            else:
                raise Exception("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._name_parse(argv)

        if task:
            data = self._get_task_data(group, subgroup, task)

            self._clock_in(data)
            self._save_task(group, subgroup, task, data)
            self._set_current(group, subgroup, task)
            self._save_current()
        else:
            print("No task specified")

    def halt(self, argv, also_conclude=False):
        group = self.current_group
        subgroup = self.current_subgroup
        task = self.current_task

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--id", '-i']:
                (group, subgroup, task) = self._id_parse(argv)
            else:
                raise Exception("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._name_parse(argv)

        if not task:
            if also_conclude:
                print("No task specified")
            else:
                print("Not working on any task")
            return

        data = self._get_task_data(group, subgroup, task)

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
        # TODO
        pass

    def list(self, argv):
        self.export(argv)

    def export(self, argv):
        all = False
        concluded = False
        verbose = False
        output = None

        group = self.current_group
        subgroup = self.current_subgroup
        task = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--concluded", "-c"]:
                concluded = True
            elif opt in ["--all", "-a"]:
                all = True
            elif opt in ["--verbose", "-v"]:
                verbose = True
            elif opt in ["--output", "-o"]:
                output = argv.pop(0)
            elif opt in ["--id", '-i']:
                (group, subgroup, task) = self._gid_parse(argv)
            else:
                raise Exception("No such option: %s" % opt)
        if len(argv) > 0:
            (group, subgroup, task) = self._gname_parse(argv)

        if output in [None, "stdout"]:
            file = sys.stdout
            fmt = 'dit'
        else:
            file = open(output, 'w')
            fmt = output.split(".")[-1]

        if fmt not in ['dit', 'org', 'json']:
            raise Exception("Unrecognized format")

        self.printer = __import__(fmt + 'printer')
        self.printer.file = file

        if all:
            self._export_all(concluded, verbose)
        elif task:
            self._export_task(group, subgroup, task, concluded, verbose)
        elif subgroup is not None:
            self._export_subgroup(group, subgroup, concluded, verbose)
        elif group is not None:
            self._export_group(group, concluded, verbose)
        else:
            print("Nothing to do")

        file.close()

    # ===========================================
    # Main

    def configure(self, argv):
        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--verbose", "-v"]:
                dit.verbose = True
            elif opt in ["--directory", "-d"]:
                dit.directory = argv.pop(0)
            elif opt in ["--help", "-h"]:
                print(__doc__)
                return False
            else:
                raise Exception("No such option: %s" % opt)
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
                self.halt()
            elif cmd in ["conclude", "c"]:
                self.conclude(argv)
            elif cmd in ["status", "q"]:
                self.status(argv)
            elif cmd in ["list", "l"]:
                self.list(argv)
            elif cmd in ["export", "e"]:
                self.export(argv)
            else:
                raise Exception("No such command: %s" % cmd)
        else:
            print("Missing command")

# ===========================================
# Main

if __name__ == "__main__":

    argv = sys.argv
    argv.pop(0)

    dit = Dit()

    if dit.configure(argv):
        dit.interpret(argv)
