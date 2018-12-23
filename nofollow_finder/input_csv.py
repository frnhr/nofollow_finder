from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import csv
import logging
import re


log = logging.getLogger(__name__)


class InputCSV(object):
    pattern = re.compile('^[a-z]{2,6}://[^/]')

    def __init__(self, file_path):
        self.file_path = file_path

    def urls(self):
        with open(self.file_path) as fh:
            reader = csv.reader(fh)
            for line_number, row in enumerate(reader, start=1):
                url = row[0]
                validated_url = self.validate(url)
                if not validated_url:
                    self.reject(line_number, url)
                else:
                    yield validated_url

    @classmethod
    def validate(cls, url):
        """Does the url look like a URL?"""
        if cls.pattern.match(url):
            return url
        return None

    @staticmethod
    def reject(line_number, url):
        log.warning(
            'input on line %d does not look like a URL, skipping: %s',
            line_number, url)
