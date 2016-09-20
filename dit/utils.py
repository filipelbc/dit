# -*- coding: utf-8 -*-

import re
import os

from getpass import getuser
from tempfile import gettempdir


def make_tmp_fp(name):
    name = re.sub(r'[^_A-Za-z0-9]', '_', name).strip('_') + '.txt'

    path = os.path.join(gettempdir(), getuser(), "dit")
    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.join(path, name)
