# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import csv
import collections
import sys

csv_row = collections.namedtuple('csv_row', 'url http_response nofollow count')


class OutputCSV(object):
    def __init__(self, out_file, overwrite=False):
        self.out_file = out_file
        self.writer = None
        self.fh = None
        self.mode = 'w' if overwrite else 'a'

    def open(self):
        if self.out_file:
            self.fh = open(self.out_file, self.mode)
        else:
            self.fh = sys.stdout
        self.writer = csv.writer(self.fh)

    def close(self):
        if self.out_file:
            self.fh.close()

    def write(self, data):
        row = csv_row(**data)
        self.writer.writerow(row)
