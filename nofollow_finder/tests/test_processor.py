#  coding=utf-8
import unittest

from nofollow_finder import processor


class UrlDataConstructorAndPatternTests(unittest.TestCase):
    def setUp(self):
        self.d = processor.UrlData(
            domains=['twitter.com', 'facebook.com'],
        )

    def test_kwargs(self):
        d = processor.UrlData(
            domains=['twitter.com', 'facebook.com'],
            url='mock_url',
            foo='bar',
        )
        self.assertEqual(['twitter.com', 'facebook.com'], d.domains)
        self.assertEqual('mock_url', d['url'])
        self.assertEqual('bar', d['foo'])

    def test_pattern_domain_1(self):
        self.d['facebook.com'] = 'FOO'
        value = self.d['domain_1']
        expected = 'FOO'
        self.assertEqual(expected, value)

    def test_pattern_domain_2(self):
        self.d['twitter.com'] = 'FOO'
        value = self.d['domain_0']
        expected = 'FOO'
        self.assertEqual(expected, value)

    def test_pattern_count_1(self):
        self.d['twitter.com_count'] = 'FOO'
        value = self.d['domain_0_count']
        expected = 'FOO'
        self.assertEqual(expected, value)

    def test_pattern_count_2(self):
        self.d['facebook.com_count'] = 'FOO'
        value = self.d['domain_1_count']
        expected = 'FOO'
        self.assertEqual(expected, value)

    def test_pattern_key_error(self):
        with self.assertRaises(KeyError):
            # noinspection PyStatementEffect
            self.d['domain_2_count']


class UrlDataUpdateTests(unittest.TestCase):
    def setUp(self):
        self.d = processor.UrlData(
            domains=['twitter.com', 'facebook.com'],
        )

    def test_empty(self):
        expected = {
            'facebook.com': 'not found',
            'facebook.com_count': 0,
            'twitter.com': 'not found',
            'twitter.com_count': 0,
        }
        value = self.d.copy()
        self.assertDictEqual(expected, value)

    def test_updated_nofollow(self):
        expected = {
            'facebook.com': 'nofollow',
            'facebook.com_count': 1,
            'twitter.com': 'not found',
            'twitter.com_count': 0,
        }
        self.d.add('facebook.com', True)
        value = self.d.copy()
        self.assertDictEqual(expected, value)

    def test_updated_nofollow_nofollow(self):
        expected = {
            'facebook.com': 'nofollow',
            'facebook.com_count': 2,
            'twitter.com': 'not found',
            'twitter.com_count': 0,
        }
        self.d.add('facebook.com', True)
        self.d.add('facebook.com', True)
        value = self.d.copy()
        self.assertDictEqual(expected, value)

    def test_updated_nofollow_follow(self):
        expected = {
            'facebook.com': 'follow',
            'facebook.com_count': 2,
            'twitter.com': 'not found',
            'twitter.com_count': 0,
        }
        self.d.add('facebook.com', True)
        self.d.add('facebook.com', False)
        value = self.d.copy()
        self.assertDictEqual(expected, value)

    def test_set_failure(self):
        expected = {
            'facebook.com': 'Fail',
            'facebook.com_count': 0,
            'twitter.com': 'Fail',
            'twitter.com_count': 0,
        }
        self.d.set_failure()
        value = self.d.copy()
        self.assertDictEqual(expected, value)


class UrlDataDataTest(unittest.TestCase):
    def test_empty(self):
        d = processor.UrlData(domains=[], url='foo', http_response='bar')
        expected = {'url': 'foo', 'http_response': 'bar'}
        self.assertEqual(expected, d.data)

    def test_zeroes(self):
        d = processor.UrlData(url='foo', http_response='bar',
                              domains=['twitter.com', 'facebook.com'])
        expected = {
            'domain_0': 'not found',
            'domain_0_count': 0,
            'domain_1': 'not found',
            'domain_1_count': 0,
            'url': 'foo',
            'http_response': 'bar'
        }
        self.assertEqual(expected, d.data)

    def test_failure(self):
        d = processor.UrlData(url='foo', http_response='bar',
                              domains=['twitter.com', 'facebook.com'])
        d.set_failure()
        expected = {
            'domain_0': 'Fail',
            'domain_0_count': 0,
            'domain_1': 'Fail',
            'domain_1_count': 0,
            'url': 'foo',
            'http_response': 'bar'
        }
        self.assertEqual(expected, d.data)

    def test_nofollow_nofollow(self):
        d = processor.UrlData(url='foo', http_response='bar',
                              domains=['twitter.com', 'facebook.com'])
        d.add('facebook.com', True)
        d.add('facebook.com', True)
        expected = {
            'domain_0': 'not found',
            'domain_0_count': 0,
            'domain_1': 'nofollow',
            'domain_1_count': 2,
            'url': 'foo',
            'http_response': 'bar'
        }
        self.assertEqual(expected, d.data)

    def test_nofollow_follow(self):
        d = processor.UrlData(url='foo', http_response='bar',
                              domains=['twitter.com', 'facebook.com'])
        d.add('facebook.com', True)
        d.add('facebook.com', False)
        expected = {
            'domain_0': 'not found',
            'domain_0_count': 0,
            'domain_1': 'follow',
            'domain_1_count': 2,
            'url': 'foo',
            'http_response': 'bar'
        }
        self.assertEqual(expected, d.data)

    def test_follow_nofollow(self):
        d = processor.UrlData(url='foo', http_response='bar',
                              domains=['twitter.com', 'facebook.com'])
        d.add('facebook.com', False)
        d.add('facebook.com', True)
        expected = {
            'domain_0': 'not found',
            'domain_0_count': 0,
            'domain_1': 'follow',
            'domain_1_count': 2,
            'url': 'foo',
            'http_response': 'bar'
        }
        self.assertEqual(expected, d.data)
