# -*- coding: utf-8 -*-

import os

from dit.common import load_json_file, save_json_file, INDEX_FN


class Index():
    fp = None
    data = []

    def load(self, path):
        self.fp = os.path.join(path, INDEX_FN)
        data = load_json_file(self.fp)
        if data:
            self.data = data

    def save(self):
        if self.fp:
            save_json_file(self.fp, self.data)
