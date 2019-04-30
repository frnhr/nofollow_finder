# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging

from ..input_csv import InputCSV
from ..settings import settings
from .google_search import GoogleSearch


log = logging.getLogger(__name__)


class GoogleInputCSV(InputCSV):
    MIN_TERM_LEN = 3

    def __init__(self, in_file, count):
        self.count = count
        self.google_search = GoogleSearch(
            settings.GOOGLE_API_KEY, settings.GOOGLE_API_CX)
        super(GoogleInputCSV, self).__init__(in_file)

    def links_from_row(self, row):
        term = row[0]
        term = self.validate_search_term(term)
        if not term:
            raise StopIteration()
        for result in self.google_search.get(term, self.count):
            yield {
                'url': result['link'],
                'query': term,
            }

    def validate_search_term(self, term):
        term = term.strip()
        if len(term) < self.MIN_TERM_LEN:
            log.warning('query too short, skipping: {}'.format(term))
            return None
        if not isinstance(term, unicode):
            term = term.decode('utf-8')
        return term
