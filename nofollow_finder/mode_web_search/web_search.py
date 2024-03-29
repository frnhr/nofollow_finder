# coding=utf-8
import logging


log = logging.getLogger(__name__)


class WebSearch(object):
    def __init__(self, settings, count):
        self.settings = settings
        self.count = count

    def get(self, term):
        count = self.count
        results, has_next = [], True
        for i in range(count):
            if i >= count:
                raise StopIteration()
            if not results and has_next:
                # TODO filling up the results queue could be done async
                results, has_next = self._try_query(term, num=10, offset=i)
            if not results:
                raise StopIteration()
            yield self._get_url(results.pop(0))

    def _try_query(self, term, num, offset):
        if not isinstance(term, unicode):
            term = term.decode('utf-8')
        try:
            return self._query(term, num, offset)
        except:
            log.exception('Error accessing Search API')
            return [], False

    def _query(self, term, num, offset):
        raise NotImplementedError()

    def _get_url(self, result):
        raise NotImplementedError()
