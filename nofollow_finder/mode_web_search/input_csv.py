# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
from tempfile import NamedTemporaryFile

from nofollow_finder.mode_web_search.search_bing import BingSearch
from nofollow_finder.mode_web_search.search_google import GoogleSearch
from nofollow_finder.settings import settings
from ..input_csv import InputCSV


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


SEARCH_ENGINES = {
    'google': GoogleSearch,
    'bing': BingSearch,
}


class WebSearchInputCSV(InputCSV):
    MIN_TERM_LEN = 3

    def __init__(self, in_file, search_engines=(), counts=()):
        self.search_engines = (
            SEARCH_ENGINES[engine](settings, count)
            for engine, count in zip(search_engines, counts)
        )
        self.counts = counts

        if in_file == '+':
            tmp = NamedTemporaryFile('w+', delete=False)
            tmp.write(HARDCODED_DEFAULTS)
            in_file = tmp.name
            tmp.close
        super(WebSearchInputCSV, self).__init__(in_file)

    def web_search(self, term):
        for search_engine in self.search_engines:
            for url in search_engine.get(term):
                yield url, search_engine.slug

    def links_from_row(self, row):
        term = row[0]
        term = self.validate_search_term(term)
        if not term:
            raise StopIteration()
        for url, engine in self.web_search(term):
            yield {
                'url': url,
                'query': term,
                'engine': engine,
            }

    def validate_search_term(self, term):
        term = term.strip()
        if len(term) < self.MIN_TERM_LEN:
            log.warning('query too short, skipping: {}'.format(term))
            return None
        if not isinstance(term, unicode):
            term = term.decode('utf-8')
        return term
