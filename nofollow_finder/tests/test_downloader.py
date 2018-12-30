#  coding=utf-8
import unittest
from mock import mock

from nofollow_finder import downloader


class DownloaderTests(unittest.TestCase):

    def test_example_com(self):
        d = downloader.Downloader(timeout=7)
        code, body = d.get('http://example.com')
        self.assertEqual(
            200, code,
            'Response code is not 200. Are you connected to the internet?')
        self.assertIn(
            '<body', body,
            '<body> tag not found. Are you connected to the internet?')

    @mock.patch('nofollow_finder.downloader.log')
    def test_example_com_301(self, p_log):
        d = downloader.Downloader(follow_redirects=False, timeout=7)
        with self.assertRaises(d.GetException):
            d.get('http://facebook.com')
        p_log.error.assert_called_once_with(
            'HTTP status %d for url %s', 302, 'http://facebook.com')
