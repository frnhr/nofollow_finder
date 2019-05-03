# coding=utf-8
import logging
import urllib

import requests

from ..mode_web_search.web_search import WebSearch

log = logging.getLogger(__name__)


class GoogleSearch(WebSearch):
    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx

    def _query(self, term, num, offset):
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
