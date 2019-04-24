# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import re

import lxml

log = logging.getLogger(__name__)


STATUS_NOT_FOUND = 'not found'
STATUS_NOFOLLOW = 'nofollow'
STATUS_FOLLOW = 'follow'
STATUS_FAIL = 'Fail'


class UrlData(dict):
    pattern = re.compile('^domain_([0-9]+)(?:_count)?$')

    def __init__(self, domains, **kwargs):
        self.domains = domains
        self._data_keys = kwargs.keys()
        for domain in domains:
            self[domain] = STATUS_NOT_FOUND
            self[self._count_key(domain)] = 0
        super(UrlData, self).__init__(**kwargs)

    def set_failure(self):
        for domain in self.domains:
            self[domain] = STATUS_FAIL

    @staticmethod
    def _count_key(domain):
        return '{}_count'.format(domain)

    def inc_count(self, domain):
        self[self._count_key(domain)] += 1

    def update_status(self, domain, is_nofollow):
        nofollow_statuses = [is_nofollow]
        if self[domain] != STATUS_NOT_FOUND:
            nofollow_statuses.append(self[domain] == STATUS_NOFOLLOW)
        if all(nofollow_statuses):
            self[domain] = STATUS_NOFOLLOW
        else:
            self[domain] = STATUS_FOLLOW

    def add(self, domain, is_nofollow):
        self.inc_count(domain)
        self.update_status(domain, is_nofollow)

    def __getitem__(self, item):
        match = self.pattern.match(item)
        if not match:
            return super(UrlData, self).__getitem__(item)
        index = int(match.group(1))
        try:
            domain = self.domains[index]
        except IndexError:
            return super(UrlData, self).__getitem__(item)
        else:
            key = item.replace('domain_{}'.format(index), domain)
            return super(UrlData, self).__getitem__(key)

    @property
    def data(self):
        value = {
            key: self[key]
            for key in self._data_keys
        }
        for i, domain in enumerate(self.domains):
            value['domain_{}'.format(i)] = self[domain]
            value['domain_{}_count'.format(i)] = self[self._count_key(domain)]
        return value


class Processor(object):
    def __init__(self, input_csv, downloader, parser, output_csv):
        self.input_csv = input_csv
        self.downloader = downloader
        self.parser = parser
        self.output_csv = output_csv
        self.domains = parser.domains
        self._domain_args_ = None

    def process(self):
        log.debug('processing')
        links = self.input_csv.links()
        self.output_csv.open()
        try:
            for link in links:
                url_data = self._process_link(link)
                self.output_csv.write(url_data)
        except KeyboardInterrupt:
            log.warning('interrupt received, stopping')
            return
        finally:
            self.output_csv.close()

    def make_url_data(self, link):
        return UrlData(
            domains=self.domains,
            url=link['url'],
            http_response=0,
        )

    def _process_link(self, link):
        url = link['url']
        log.debug('url %s', url)
        url_data = self.make_url_data(link)
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
            url_data.set_failure()
        else:
            try:
                a_nodes = self.parser.find_a_nodes(html)
                for a_node, domain, has_nofollow in a_nodes:
                    self.log_a(url, a_node)
                    url_data.add(domain, has_nofollow)
            except self.parser.ZeroANodes:
                log.error('No A nodes found on %s', url)
        return url_data.data

    @staticmethod
    def log_a(url, a_node):
        html = lxml.html.tostring(a_node)
        log.info('%s - %s', url, html)
