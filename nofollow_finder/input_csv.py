# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import csv
import logging
import re
import sys

log = logging.getLogger(__name__)


class InputCSV(object):
    pattern = re.compile('^[a-z]{2,6}://[^/]')

    def __init__(self, file_path):
        self.file_path = file_path

    def urls(self):
        line_number = 0
        found_one = False
        try:
            if self.file_path:
                fh = open(self.file_path)
            else:
                fh = sys.stdin
            reader = csv.reader(fh)
            for line_number, row in enumerate(reader, start=1):
                url = row[0].decode("utf-8-sig")
                url = url.strip()
                validated_url = self.validate(url)
                if not validated_url:
                    self.reject(line_number, url)
                else:
                    found_one = True
                    yield validated_url
        finally:
            if self.file_path:
                fh.close()
        if not found_one:
            log.error('No URLs found in the first column of input file')
        if not line_number:
            log.error('Error parsing input file')

    @classmethod
    def validate(cls, url):
        """Does the url look like a URL?"""
        if cls.pattern.match(url):
            return url
        return None

    @staticmethod
    def reject(line_number, url):
        log.warning(
            'input on line %d does not look like a URL, skipping: "%s"',
            line_number, url.decode('utf-8'))
