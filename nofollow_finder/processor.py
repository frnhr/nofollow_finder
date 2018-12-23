from __future__ import(
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging

import lxml

log = logging.getLogger(__name__)


class Processor(object):
    NOFOLLOW_YES = 'Yes'
    NOFOLLOW_NO = 'No'
    NOFOLLOW_ERROR = 'Fail'

    def __init__(self, input_csv, downloader, parser, output_csv):
        self.input_csv = input_csv
        self.downloader = downloader
        self.parser = parser
        self.output_csv = output_csv

    def process(self):
        log.debug('processing')
        urls = self.input_csv.urls()
        self.output_csv.open()
        try:
            for url in urls:
                url_data = self._process_url(url)
                self.output_csv.write(url_data)
        except KeyboardInterrupt:
            log.warning('interrupt received, stopping')
            return
        finally:
            self.output_csv.close()

    def _process_url(self, url):
        log.debug('url %s', url)
        url_data = {
            'url': url,
            'nofollow': self.NOFOLLOW_NO,
            'count': 0,
            'http_response': 0,
        }
        html = ''
        # noinspection PyBroadException
        try:
            status_code, html = self.downloader.get(url)
        except self.downloader.GetException:
            log.debug('Caught GetException for url %s', url)
        except Exception:
            log.error('unexpected error while downloading url %s', url)
        else:
            url_data['http_response'] = status_code
        if not html:
            url_data['nofollow'] = self.NOFOLLOW_ERROR
            return url_data

        try:
            a_nodes = self.parser.find_a_nodes(html)
            for a_node, domain, has_nofollow in a_nodes:
                self.log_a(url, a_node)
                if has_nofollow:
                    url_data['count'] += 1
                    url_data['nofollow'] = self.NOFOLLOW_YES
        except self.parser.ZeroANodes:
            log.error('No A nodes found on %s', url)
        return url_data

    @staticmethod
    def log_a(url, a_node):
        html = lxml.html.tostring(a_node)
        log.info('%s - %s', url, html)
