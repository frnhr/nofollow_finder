# coding=utf-8
import logging
import urllib

import requests


log = logging.getLogger(__name__)


class GoogleSearch(object):
    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx

    def get(self, term, count=14):
        results, has_next = [], True
        for i in range(count):
            if i >= count:
                raise StopIteration()
            if not results and has_next:
                # TODO filling up the results queue could be done async
                results, has_next = self._try_query(term, num=10, offset=i)
            if not results:
                raise StopIteration()
            yield results.pop(0)

    def _try_query(self, term, num, offset):
        try:
            return self._query(term, num, offset)
        except:
            log.exception('Error accessing Google Custom Search API')
            return [], False

    def _query(self, term, num, offset):
        if not isinstance(term, unicode):
            term = term.decode('utf-8')
        log.debug(u'_query for "{}", n={}, offset={}'.format(
            term, num, offset))
        query_params = urllib.urlencode({
            'key': self.api_key,
            'cx': self.cx,
            'q': term.encode('utf-8'),
            'num': num,
            'start': offset + 1,
        })
        data = requests.get(
            'https://www.googleapis.com/customsearch/v1?{}'.format(
                query_params)).json()
        if data.get('error'):
            log.error('Google API Error: {}'.format(data['error']))
            return [], False
        results = data.get('items', [])
        has_next = bool(data['queries'].get('nextPage'))
        log.debug(u'results: len(results)={}, has_next={}'.format(
            len(results), has_next))
        return results, has_next
