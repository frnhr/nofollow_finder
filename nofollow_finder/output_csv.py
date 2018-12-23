from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)


class OutputCSV(object):
    def __init__(self, out_file):
        self.out_file = out_file

    def open(self):
        pass

    def close(self):
        pass

    def write(self, url_data):
        pass
