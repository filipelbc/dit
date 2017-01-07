# -*- coding: utf-8 -*-

import json
import os

# ===========================================
# Constants

INDEX_FN = 'INDEX'

SEPARATOR_CHAR = '/'
NONE_CHAR = '_'
ROOT_NAME_CHAR = '.'
ROOT_NAME = ''

DEFAULT_BASE_DIR = '.dit'
DEFAULT_BASE_PATH = '~/' + DEFAULT_BASE_DIR

SELECT_BACKWARD = "forward"
SELECT_FORWARD = "backward"

# ===========================================
# Json Helpers


def load_json_file(fp):
    if os.path.isfile(fp):
        with open(fp, 'r') as f:
            return json.load(f)
    return None


def save_json_file(fp, data):
    with open(fp, 'w') as f:
        f.write(json.dumps(data))

# ===========================================
# String Helpers


def path_to_string(path):
    if path == os.path.expanduser(DEFAULT_BASE_PATH):
        return DEFAULT_BASE_PATH
    return os.path.relpath(path)


def name_to_string(name):
    if name is None:
        return NONE_CHAR
    elif name == ROOT_NAME:
        return ROOT_NAME_CHAR
    return name


def names_to_string(name, *more_names):
    s = name_to_string(name)
    for name in more_names:
        s += SEPARATOR_CHAR + name_to_string(name)
    return s

# ===========================================
# Selector Helpers


def selector_clean_root(names):
    return [name if name != ROOT_NAME_CHAR else ROOT_NAME for name in names]


def selector_split(string):
    return selector_clean_root(string.split(SEPARATOR_CHAR))

# ===========================================
# Path Helpers


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
