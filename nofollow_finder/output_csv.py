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


class OutputCSV(object):
    def __init__(self, out_file, domains, overwrite=False, header=None):
        self.domains = domains
        self.out_file = out_file
        self.writer = None
        self.fh = None
        self.mode = 'w' if overwrite else 'a'
        self.header = header if header is not None else overwrite
        self._csv_row = None

    @property
    def csv_row(self):
        if self._csv_row is None:
            domain_cols = ' '.join([
                'domain_{i} domain_{i}_count'.format(i=i)
                for i, _ in enumerate(self.domains)
            ])
            if domain_cols:
                domain_cols = ' {}'.format(domain_cols)
            self._csv_row = collections.namedtuple(
                'csv_row', 'url http_response{}'.format(domain_cols))
        return self._csv_row

    def header_row(self):
        header = ['URL', 'HTTP response code']
        for domain in self.domains:
            header.append(domain)
            header.append('{} count'.format(domain))
        return self.csv_row(*header)

    def open(self):
        if self.out_file:
            self.fh = open(self.out_file, self.mode)
        else:
            self.fh = sys.stdout
        self.writer = csv.writer(self.fh)
        if self.header:
            self.writer.writerow(self.header_row())

    def close(self):
        if self.out_file:
            self.fh.close()

    def write(self, data):
        row = self.csv_row(**data)
        self.writer.writerow(row)
        self.fh.flush()
