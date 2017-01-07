# -*- coding: utf-8 -*-

import os

from . import messages as msg
from .exceptions import DitError

from .common import (
    INDEX_FN,
    ROOT_NAME,
    load_json_file,
    save_json_file,
    is_valid_task_name,
)

INITIAL_DATA = [[ROOT_NAME, [[ROOT_NAME, []]]]]


class Index():
    base_path = None
    fp = None
    data = INITIAL_DATA

    def load(self, base_path):
        self.base_path = base_path
        self.fp = os.path.join(self.base_path, INDEX_FN)
        data = load_json_file(self.fp)
        if data:
            self.data = data

    def save(self):
        if self.fp:
            save_json_file(self.fp, self.data)
            msg.verbose("INDEX saved.")

    def add(self, group, subgroup, task):
        group_id = -1
        for i in range(len(self.data)):
            if self.data[i][0] == group:
                group_id = i
                break
        if group_id == -1:
            group_id = len(self.data)
            self.data.append([group, [[ROOT_NAME, []]]])

        subgroup_id = -1
        for i in range(len(self.data[group_id][1])):
            if self.data[group_id][1][i][0] == subgroup:
                subgroup_id = i
                break
        if subgroup_id == -1:
            subgroup_id = len(self.data[group_id][1])
            self.data[group_id][1].append([subgroup, []])

        self.data[group_id][1][subgroup_id][1].append(task)

    def remove(self, group, subgroup, task):
        for g in self.data:
            if g[0] == group:
                for s in g[1]:
                    if s[0] == subgroup:
                        for k, t in enumerate(s[1]):
                            if t == task:
                                s[1][k] = None
                                break
                        break
                break

    def rebuild(self):
        self.data = INITIAL_DATA
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
                    self.data.append([group, [[ROOT_NAME, []]]])

                if subgroup != c_subgroup:
                    c_subgroup = subgroup
                    self.data[-1][1].append([subgroup, []])

                self.data[-1][1][-1][1].append(f)
        msg.verbose("INDEX rebuilt.")

    def idxs_to_names(self, idxs):
        if len(idxs) < 3:
            raise DitError("Invalid index format.")

        names = [None] * 3
        try:
            index = self.data
            for i, idx in enumerate(idxs):
                if idx is None:  # we can no longer navigate the index
                    break
                idx = int(idx)
                if i < 2:  # it is a group or subgroup
                    names[i] = index[idx][0]
                    index = index[idx][1]  # navigate the index further
                else:  # it is a task
                    names[i] = index[idx]
        except ValueError:
            raise DitError("Invalid index format, must be an integer: %s" % idx)
        except IndexError:
            raise DitError("Invalid index: %d" % idx)

        return names

    def __iter__(self):
        return self.data.__iter__()
