# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import re

from lxml.etree import (
    ParserError,
)
from pyquery import (
    PyQuery,
)


log = logging.getLogger(__name__)


class Parser(object):
    a_selector = 'a[href]'
    pattern_template = (
        '^'  # start of string
        '(?:'  # open a non-capturing group
        'https?:'  # "http:" or "https:"
        ')?'  # close the non-capturing group and make it optional 
        '//'  # literally two slashes, required
        '('  # open a capturing group
        '{domains}'  # generated pattern, see self.domains_pattern() below
        ')'  # close the capturing group
        '(?:'  # open a non-capturing group
        '/?|/.*'  # first thing after domain can be end-of-string or / 
        ')'  # close the non-capturing group
        '$'
    )
    subdomain_pattern = (
        '(?:'  # open non-capture group "OUTER"
        '(?:'  # open another non-capture group "LABELS"
        '[^./]{1,63}'  # single label with up to 63 chars
        '\.'  # a dot
        ')'  # close non-capture group "LABELS"
        '{0,2}'  # group "LABELS" can repeat 0 to 2 times
        ')'  # close non-capture group "OUTER"
        '?'  # make the whole "OUTER" group optional
    )

    class ZeroANodes(Exception):
        """No A tags found"""

    def __init__(self, domains):
        self.domains = domains
        self._re = re.compile(self.full_pattern)

    @property
    def domains_pattern(self):
        domains_patterns = [
            '({}{})'.format(self.subdomain_pattern, re.escape(domain))
            for domain in self.domains
        ]
        pattern = '|'.join(domains_patterns)
        log.debug('domains pattern: %s', pattern)
        return pattern

    @property
    def full_pattern(self):
        pattern = self.pattern_template.format(
            domains=self.domains_pattern,
        )
        log.debug('full pattern: %s', pattern)
        return pattern

    def find_a_nodes(self, html):
        log.debug('finding a nodes')
        for a_node in self._a_nodes(html):
            domain = self._matches_domain(a_node)
            if domain:
                yield a_node, domain, self._is_nofollow(a_node)

    def _matches_domain(self, a_node):
        href = a_node.attrib['href']
        match = self._re.match(href)
        if match:
            domain = match.group(1)
            log.debug('match: %s', href)
        else:
            domain = None
        return domain

    @staticmethod
    def _is_nofollow(a_node):
        match = ''.join([
            a_node.attrib.get('rel', ''),
            a_node.attrib.get('Rel', ''),
            a_node.attrib.get('REL', ''),
        ]).lower().strip() == 'nofollow'
        return match

    def _a_nodes(self, html):
        try:
            d = PyQuery(html)  # "d" like "$" (dollar sign, jQuery!!)
        except ParserError:
            log.error('')
            raise StopIteration()
        found_one = False
        for a in d(self.a_selector):
            found_one = True
            yield a
        if not found_one:
            raise self.ZeroANodes()
