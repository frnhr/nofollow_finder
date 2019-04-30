# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
from tempfile import NamedTemporaryFile

from ..input_csv import InputCSV
from ..settings import settings
from .google_search import GoogleSearch


log = logging.getLogger(__name__)

HARDCODED_DEFAULTS = '''
Homework
english homework
economics homework help
chemistry help
psychology questions and answers
homework help online
biology answers
philosophy questions and answers
physics answers
accounting help
history homework help
essay writing service
essay writer
accounting help
math homework
statistics help
aleks answers
mymathlab answers
mystatlab answers
zybooks answers
writing help
girl wash your face summary
art of the deal summary
things fall apart setting
bad blood book
educated a memoir
Literature Study Guides
Studypool, Homework Help
Chemistry Answers
accounting homework help
accounting homework
accounting help
aleks answers
Alice In Wonderland
art of the deal study guide
bad blood study guide
biology homework answers
chemistry help
chemistry homework
chemistry homework help
qualified homework help
homework help answers
psychology homework answers
english homework help
psychology question and answers
psychology answers
girl wash your face study guide
'''.strip()


class GoogleInputCSV(InputCSV):
    MIN_TERM_LEN = 3

    def __init__(self, in_file, count):
        self.count = count
        self.google_search = GoogleSearch(
            settings.GOOGLE_API_KEY, settings.GOOGLE_API_CX)
        if in_file == '+':
            tmp = NamedTemporaryFile('w+', delete=False)
            tmp.write(HARDCODED_DEFAULTS)
            in_file = tmp.name
            tmp.close
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
