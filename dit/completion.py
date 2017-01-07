# -*- coding: utf-8 -*-

import os

from .common import (
    ROOT_NAME_CHAR,
    SELECT_BACKWARD,
    SELECT_FORWARD,
    SEPARATOR_CHAR,
    discover_base_path,
    load_json_file,
    names_to_string,
    selector_split,
)

# ===========================================
# Constants

COMPLETION_SEP_CHAR = '\n'
COMMAND_INFO_FN = 'command_info.json'

DIT_OPTIONS = [
    "--check-hooks",
    "--directory",
    "--help",
    "--no-hooks",
    "--verbose",
]

# ===========================================
# Helpers


def _load_command_info():
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      COMMAND_INFO_FN)
    return load_json_file(fp)


def _save_command_info():
    from dit.dit import COMMAND_INFO
    from dit.common import save_json_file

    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      COMMAND_INFO_FN)
    save_json_file(fp, COMMAND_INFO)

# ===========================================
# Completion Modes


def _gname(index, names):
    _ = names_to_string

    names[-1] = None
    names = names + [None] * (3 - len(names))
    (group, subgroup, task) = names

    comp_options = []
    for i, g in enumerate(index):
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

    return COMPLETION_SEP_CHAR.join(comp_options)


def _selection(cmd, cmd_info, directory, selection):

    names = selector_split(selection)
    if len(names) > 3:
        return ""

    path = discover_base_path(directory)
    if not os.path.exists(path):
        return ""

    from dit.index import Index
    index = Index()
    index.load(path)
    if not index.data:
        return ""

    select = cmd_info[cmd]['select']

    if select in [SELECT_FORWARD, SELECT_BACKWARD]:
        return _gname(index.data, names)
    else:
        return ""


def _cmd_name(cmd_info):
    return COMPLETION_SEP_CHAR.join([cmd for cmd in cmd_info])


def _cmd_option(cmd, cmd_info):
    return COMPLETION_SEP_CHAR.join(cmd_info[cmd]['options'])


def _dit_option():
    return COMPLETION_SEP_CHAR.join(DIT_OPTIONS)

# ===========================================
# Entry point


def interpret(argv):
    idx = int(argv.pop(0)) - 1
    line = argv[1:]
    cmd = None
    directory = None

    i = 0
    while i != idx and i < len(line):
        if line[i] in ['--directory', '-d']:
            i += 1
            directory = line[i]
        elif line[i].isalpha():
            cmd = line[i]
            break
        i += 1

    cmd_info = _load_command_info()
    if cmd and cmd not in cmd_info:
        return ""

    word = line[idx] if len(line) > idx else ""
    comp_options = ""

    if word == "" or word[0].isalpha():
        if cmd:
            comp_options = _selection(cmd, cmd_info, directory, word)
        else:
            comp_options = _cmd_name(cmd_info)
    elif word.startswith((ROOT_NAME_CHAR, SEPARATOR_CHAR)):
        if cmd:
            comp_options = _selection(cmd, cmd_info, directory, word)
    elif word.startswith('-'):
        if cmd:
            comp_options = _cmd_option(cmd, cmd_info)
        else:
            comp_options = _dit_option()

    return comp_options
