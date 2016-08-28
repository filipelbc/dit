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

    status [<id> | <name>]
      Prints current task.

    list [<id> | <name>] [--all, -a] [--concluded, -c]
      Lists a group, subgroup, or task. If none specified, lists current subgroup.
      --all, -a
        Lists all groups and subgroups.
      --concluded, -a
        Include concluded tasks in the listing.

    export [org]

  <name>: ["group-name".]["subgroup-name".]"task-name"

  <id>: --id, -i ["group-id".]["subgroup-id".]"task-id"

      Uses current group and current subgroup if they are not specified.
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

    current_group = None
    current_subgroup = None
    current_task = None

    index = [[None, [[None, []]]]]

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
    def _get_task_data_fn(fn):
        if not os.path.isfile(fn):
            raise Exception("Is not a file: %s" % fn)

        with open(fn, 'r') as f:
            return json.load(f)

    def _get_task_data(self, group, subgroup, task):
        fn = self._task_path(group, subgroup, task)

        return self._get_task_data_fn(fn)

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

    @staticmethod
    def _print_task(task, data, verbose):
        print("\n~ %s" % task)

        description = data['description']
        print("  `%s`" % description)

        notes = data['notes']
        if notes:
            print("  %sNotes:")
        for note in notes:
            print("    * %s" % note)

        props = data['properties']
        if props:
            print("  %sproperties:")
        for prop in props:
            print("    * %s" % prop)

    def _list_task(self, subgroup_path, task, concluded, verbose=False):
        fn = os.path.join(subgroup_path, task)
        data = self._get_task_data_fn(fn)

        if not data.get('concluded_at', None) or concluded:
            self._print_task(task, data, verbose)

    def _list(self, group, subgroup, concluded):

        subgroup_path = self._subgroup_path(group, subgroup)

        print("# %s/%s" % (group, subgroup))

        for task in os.listdir(subgroup_path):
            self._list_task(subgroup_path, task, concluded)

    # def _list_all(concluded):
    #     subgroups = []
    #     for x in os.listdir(group_path):
    #         if os.path.isdir(os.path.join(group_path, x))
    #             subgroups.append(x)

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

    def _id_parse(self, argv):
        ids = argv.pop(0).split('.')
        # TODO

        group = None
        subgroup = None
        task = None

        return (group, subgroup, task)

    #     if len(ids) in [3, 2]:
    #         group_id = ids.pop(0)
    #         group = self.index[group_id][0]
    #     else:
    #         group = self.current_group
    #         group_id =

    #     if len(ids) == 2:
    #         subgroup_id = ids.pop(0)
    #         subgroup = self.index[group_id][0]
    #     else:
    #         subgroup = self.current_subgroup

    #     task_id = ids.pop(0)
    #     task = s

    #     return (group, subgroup, task)

    def _name_parse(self, argv):
        names = argv.pop(0).split('.')

        if len(names) in [3, 2]:
            group = names.pop(0)
        else:
            group = self.current_group

        if len(names) == 2:
            subgroup = names.pop(0)
        else:
            subgroup = self.current_subgroup

        task = names.pop(0)

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

        opt = argv.pop(0)
        if opt in ["--new", "-n"]:
            (group, subgroup, task) = self.new(argv)
        elif opt in ["--id", '-i']:
            (group, subgroup, task) = self._id_parse(argv)
        else:
            (group, subgroup, task) = self._name_parse(argv)

        data = self._get_task_data(group, subgroup, task)

        self._clock_in(data)
        self._save_task(group, subgroup, task, data)
        self._set_current(group, subgroup, task)
        self._save_current()

    def halt(self, argv, also_conclude=False):
        if len(argv) > 0:
            opt = argv.pop(0)
            if opt in ["--id", '-i']:
                (group, subgroup, task) = self._id_parse(argv)
            else:
                (group, subgroup, task) = self._name_parse(argv)
        else:
            group = self.current_group
            subgroup = self.current_subgroup
            task = self.current_task

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
        all = False
        concluded = False

        group = self.current_group
        subgroup = self.current_subgroup

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--group", "-g"]:
                group = argv.pop(0)
            elif opt in ["--subgroup", "-s"]:
                subgroup = argv.pop(0)
            elif opt in ["--concluded", "-c"]:
                concluded = True
            elif opt in ["--all", "-a"]:
                all = True
            elif opt in ["--verbose", "-v"]:
                verbose = True
            else:
                raise Exception("No such option: %s" % opt)

        if all:
            self._list_all(concluded, verbose)
        else:
            self._list(group, subgroup, concluded, verbose)

    def export(self, argv):
        # TODO
        pass

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
