# coding=utf-8
import logging
import urllib

import requests

from ..mode_web_search.web_search import WebSearch

log = logging.getLogger(__name__)


class BingSearch(WebSearch):
    slug = 'bing'

    def _query(self, term, num, offset):
        log.debug(u'_query for "{}", n={}, offset={}'.format(
            term, num, offset))
        query_params = urllib.urlencode({
            'q': term.encode('utf-8'),
            'count': num,
            'offset': offset,
            'responseFilter': 'webpages',
        })
        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
        }
        data = requests.get(
            'https://api.cognitive.microsoft.com/bing/v7.0/search?{}'.format(
                query_params),
            headers=headers,
        ).json()
        if data.get('error'):
            log.error('Bing API Error: {}'.format(data['error']))
            return [], False
        results = data.get('webPages', {}).get('value', [])
        try:
            total_matches = data['webPages']['totalEstimatedMatches']
        except KeyError:
            log.warning('Failed to get totalEstimatedMatches')
            has_next = False
        else:
            last_on_page = offset + len(results)
            has_next = last_on_page < total_matches
        log.debug(u'results: len(results)={}, has_next={}'.format(
            len(results), has_next))
        return results, has_next

    @property
    def api_key(self):
        return self.settings.BING_API_KEY

    def _get_url(self, result):
        return result['url']
