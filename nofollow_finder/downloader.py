# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging

from nofollow_finder import command


log = logging.getLogger(__name__)


class Downloader(object):

    class GetException(Exception):
        """GET request failed"""

    def __init__(self, follow_redirects=True, timeout=None):
        log.debug('follow_redirects: %d', follow_redirects)
        self.follow_redirects = follow_redirects
        self.timeout = timeout

    def get(self, url):
        log.debug('get: %s', url)
        out, err = self._raw_get(url)
        body, status_code = self._split(out)
        self._validate_status(status_code, url)
        log.debug('received %s', url)
        return status_code, body

    def _raw_get(self, url):
        cmd = 'curl -w"%{{http_code}}"{follow} {url}'.format(
            follow=' -L' if self.follow_redirects else '',
            url=url,
        )
        log.debug('command: %s', cmd)
        try:
            returncode, out, err = command.run(cmd, timeout=self.timeout)
        except command.Timeout:
            log.error('curl timed out for %s', url)
            raise self.GetException()
        if returncode:
            log.error('curl returned error code %d for %s', returncode, url)
            raise self.GetException()
        return out, err

    @classmethod
    def _split(cls, out):
        out = out.decode('utf-8')
        status_code = out[-3:]
        body = out[:-3]
        try:
            status_code = int(status_code)
        except (ValueError, TypeError):
            log.info('cannot parse status code, end: %s', out[-80:])
            raise cls.GetException()
        return body, status_code

    def _validate_status(self, status_code, url):
        if status_code != 200:
            log.error('HTTP status %d for url %s', status_code, url)
            raise self.GetException()
