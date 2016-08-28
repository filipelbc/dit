#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:        Filipe L B Correia <filipelbc@gmail.com>
# Last Change:   2016 Ago 27 19:06:00
#
# About:         Command line work time tracking and todo list
#
# =============================================================================

"""
Usage: dit [--verbose] [--directory "path"] <command>

    new "id" [--group "id"] [--subgroup "id"]

    workon [--new] "id" [--group "id"] [--subgroup "id"]

    halt

    switchto [--new] "id" [--group "id"] [--subgroup "id"]

    conclude ["id"]  [--group "id"] [--subgroup "id"]

    list [--group "id"] [--subgroup "id"] [--all]

    status

    export [org]
"""

import sys
import json
import os

from pprint import PrettyPrinter
from datetime import datetime

pprint = PrettyPrinter(indent=4).pprint

# ==============
# Options


class Dit:
    directory = "~/dit"
    current_fn = "CURRENT"
    index_fn = "INDEX"

    current_group = None
    current_subgroup = None
    current_task = None

    index = [["", [["", []]]]]

    # ========================
    # Paths and files names

    def _base_path(self):
        path = os.path.expanduser(os.path.join(self.directory))
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _current_path(self):
        path = self._base_path()
        return os.path.join(path, self.current_fn)

    def _index_path(self):
        path = self._base_path()
        return os.path.join(path, self.index_fn)

    def _subgroup_path(self, group, subgroup):
        if not group:
            group = ""
        if not subgroup:
            subgroup = ""
        return os.path.join(self._base_path(), group, subgroup)

    def _task_path(self, group, subgroup, task):

        path = self._subgroup_path(group, subgroup)
        if not os.path.exists(path):
            os.makedirs(path)

        if not task:
            raise Exception("Invalid task")

        return os.path.join(path, task)

    # ============
    # Auxiliary

    @staticmethod
    def _new_task(description=None):
        return {
            "description": description,
            "logbook": [],
            "properties": [],
            "notes": [],
            "created_at": str(datetime.now())
        }

    def _create_task(self, group, subgroup, task, description=None):
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
            self.index.append([group, [["", []]]])

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

    # ==========
    # Clock

    def _clock_in(self, data):
        if data['logbook']:
            last = data['logbook'][-1]
            if not last['out']:
                print("Already clocked in")
                return

        data['logbook'] += [{'in': str(datetime.now()), 'out': None}]

    def _clock_out(self, data):
        if not data['logbook']:
            print("Already clocked out")
            return
        last = data['logbook'][-1]
        if last['out']:
            print("Already clocked out")
            return

        last['out'] = str(datetime.now())

    def _conclude(self, data):

        concluded_at = data.get('concluded_at', None)

        if concluded_at:
            print("Already concluded")
            return

        data['concluded_at'] = str(datetime.now())

    # ===========
    # Commands

    def new(self, argv):
        if len(argv) < 1:
            raise Exception("Missing argument")

        group = self.current_group
        subgroup = self.current_subgroup

        task = argv.pop(0)

        description = None

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--group", "-g"]:
                group = argv.pop(0)
            elif opt in ["--subgroup", "-s"]:
                subgroup = argv.pop(0)
            elif opt in ["--description", "-d"]:
                description = argv.pop(0)
            else:
                raise Exception("No such option: %s" % opt)

        self._create_task(group, subgroup, task, description)

    def workon(self, argv):
        if len(argv) < 1:
            raise Exception("Missing argument")

        group = self.current_group
        subgroup = self.current_subgroup

        task = argv.pop(0)

        if len(argv) > 0 and argv[0] in ["--new", "-n"]:
            argv[0] = task
            self.new(argv)

        else:
            while len(argv) > 0 and argv[0].startswith("-"):
                opt = argv.pop(0)
                if opt in ["--group", "-g"]:
                    group = argv.pop(0)
                elif opt in ["--subgroup", "-s"]:
                    subgroup = argv.pop(0)
                else:
                    raise Exception("No such option: %s" % opt)

        data = self._get_task_data(group, subgroup, task)

        self._clock_in(data)

        self._save_task(group, subgroup, task, data)

        self._set_current(group, subgroup, task)

        self._save_current()

    def halt(self):

        group = self.current_group
        subgroup = self.current_subgroup
        task = self.current_task

        if not task:
            print("Not working on any task")
            return

        data = self._get_task_data(group, subgroup, task)

        self._clock_out(data)

        self._save_task(group, subgroup, task, data)

        self.current_task = None

        self._save_current()

    def switchto(self, argv):
        self.halt()
        self.workon(argv)

    def conclude(self, argv):
        group = self.current_group
        subgroup = self.current_subgroup

        task = self.current_subgroup
        if len(argv) > 0:
            task = argv.pop(0)

        while len(argv) > 0 and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ["--group", "-g"]:
                group = argv.pop(0)
            elif opt in ["--subgroup", "-s"]:
                subgroup = argv.pop(0)
            else:
                raise Exception("No such option: %s" % opt)

        data = self._get_task_data(group, subgroup, task)

        self._clock_out(data)
        self._conclude(data)
        self._save_task(group, subgroup, task, data)

        if task == self.current_task:
            self.current_task = None
            self._save_current()

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

    # ========
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
            else:
                raise Exception("No such option: %s" % opt)
        self._load_current()
        self._load_index()

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
            elif cmd in ["list", "l"]:
                self.list(argv)
            else:
                raise Exception("No such command: %s" % cmd)
        else:
            print("Missing command")
            return

# ===============
# Main

if __name__ == "__main__":

    argv = sys.argv
    argv.pop(0)

    dit = Dit()

    dit.configure(argv)

    dit.interpret(argv)
