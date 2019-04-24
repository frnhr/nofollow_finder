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

    def links(self):
        line_number = 0
        found_one = False
        try:
            if self.file_path:
                fh = open(self.file_path)
            else:
                fh = sys.stdin
            reader = csv.reader(fh)
            for line_number, row in enumerate(reader, start=1):
                links = self.links_from_row(row)
                for link in links:
                    validated_link = self.validate(link)
                    if not validated_link:
                        self.reject(line_number, link)
                    else:
                        found_one = True
                        yield validated_link
        finally:
            if self.file_path:
                fh.close()
        if not found_one:
            log.error('No URLs found in the first column of input file')
        if not line_number:
            log.error('Error parsing input file')

    def links_from_row(self, row):
        url = row[0].decode("utf-8-sig")
        url = url.strip()
        return [{'url': url}]

    @classmethod
    def validate(cls, link):
        """Does the url look like a URL?"""
        if cls.pattern.match(link['url']):
            return link
        return None

    @staticmethod
    def reject(line_number, link):
        log.warning(
            'input on line %d does not look like a URL, skipping: "%s"',
            line_number, link['url'].decode('utf-8'))
