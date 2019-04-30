#  coding=utf-8
import unittest

from docopt import DocoptExit
from mock import mock

from nofollow_finder import __main__ as main


class CLITests(unittest.TestCase):
    def setUp(self):
        self.defaults = {
            'header': False,
            'in_file': None,
            'log_file': None,
            'out_file': None,
            'overwrite': True,
            'redirect': True,
            'timeout': 60,
            'verbosity': 3,
            'mode': None,
            'settings_file': u'.nofollowfinderrc,~/.nofollowfinderrc',
        }

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_default(self, p_sys, p_main):
        p_sys.argv = []
        with self.assertRaises(DocoptExit):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_min_valid(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com,example.net',
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com', 'example.net']
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_verbosity_and_input(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '-V', '1', '-i', 'SampleLinks.csv',
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['verbosity'] = 1
        expected['in_file'] = 'SampleLinks.csv'
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_invalid_verbosity(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '-V', '7',
        ]
        msg = 'Verbosity not one of: 0, 1, 2, 3, 4'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_invalid_file(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '-i', 'foo.csv',
        ]
        msg = 'Input file does not exist.'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_nofollow(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--nofollow',
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['redirect'] = False
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_log(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--log', 'foo.log'
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['log_file'] = 'foo.log'
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--timeout', '123'
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['timeout'] = 123
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_0(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--timeout', '0'
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['timeout'] = 0
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_negative(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--timeout', '-1',
        ]
        msg = 'Timeout has to be 0 or greater.'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_huge(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--timeout', '10123',
        ]
        msg = 'Timeout has to be 300 or less.'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_a_poem(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--timeout', 'Tomorrow keeps turning around'
        ]
        msg = 'Timeout has to be a number.'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv'
        ]
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['out_file'] = 'out.csv'
        expected['overwrite'] = True
        expected['header'] = True
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.os.path.isfile')
    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out_append(self, p_sys, p_main, p_isfile):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv', '--append',
        ]
        p_isfile.return_value = True
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['out_file'] = 'out.csv'
        expected['header'] = False
        expected['overwrite'] = False
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.os.path.isfile')
    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out_append_but_new(self, p_sys, p_main, p_isfile):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv', '--append',
        ]
        p_isfile.return_value = False
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['out_file'] = 'out.csv'
        expected['header'] = True
        expected['overwrite'] = False
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.os.path.isfile')
    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out_append_but_new_but_no_header(
            self, p_sys, p_main, p_isfile):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv', '--append', '-n',
        ]
        p_isfile.return_value = False
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['out_file'] = 'out.csv'
        expected['header'] = False
        expected['overwrite'] = False
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.os.path.isfile')
    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out_append_but_yes_header(
            self, p_sys, p_main, p_isfile):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv', '--append', '-e',
        ]
        p_isfile.return_value = True
        expected = self.defaults.copy()
        expected['domains'] = ['example.com']
        expected['out_file'] = 'out.csv'
        expected['header'] = True
        expected['overwrite'] = False
        main.run_from_cli()
        p_main.assert_called_once_with(**expected)

    @mock.patch('nofollow_finder.__main__.os.path.isfile')
    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_timeout_out_exists(self, p_sys, p_main, p_isfile):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--out', 'out.csv'
        ]
        p_isfile.return_value = True
        msg = 'Output file already exists. Overwrite: "-f" or append: "-a"'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()

    @mock.patch('nofollow_finder.__main__.main')
    @mock.patch('docopt.sys')
    def test_yesheader_noheader_omg_what(self, p_sys, p_main):
        p_sys.argv = [
            'script.py', '-d', 'example.com',
            '--header', '--noheader'
        ]
        msg = 'Specify either -e or -n but not both.'
        with self.assertRaisesRegexp(DocoptExit, msg):
            main.run_from_cli()
        p_main.assert_not_called()


class TestMain(unittest.TestCase):

    @mock.patch('nofollow_finder.__main__.InputCSV')
    @mock.patch('nofollow_finder.__main__.OutputCSV')
    @mock.patch('nofollow_finder.__main__.Downloader')
    @mock.patch('nofollow_finder.__main__.Parser')
    @mock.patch('nofollow_finder.__main__.Processor')
    @mock.patch('nofollow_finder.__main__.log')
    def test_main_default(
            self, p_log, p_processor, p_parser, p_downloader, p_output,
            p_input):
        main.main(
            'in_file.csv', ['example.com'], 'log_file.log', 'out_file.csv',
            overwrite=True, header=False, verbosity=3, redirect=True,
            timeout=2, settings_file=False, mode=False,
        )
        p_input.assert_called_once_with('in_file.csv')
        p_output.assert_called_once_with(
            'out_file.csv', ['example.com'], True, False)
        p_downloader.assert_called_once_with(follow_redirects=True, timeout=2)
        p_parser.assert_called_once_with(['example.com'])
        p_processor.assert_called_once_with(
            p_input.return_value,
            p_downloader.return_value,
            p_parser.return_value,
            p_output.return_value,
        )
        p_processor.return_value.process.assert_called_once_with()
        p_log.debug.assert_called()
        p_log.error.assert_not_called()

    @mock.patch('nofollow_finder.__main__.InputCSV')
    @mock.patch('nofollow_finder.__main__.OutputCSV')
    @mock.patch('nofollow_finder.__main__.Downloader')
    @mock.patch('nofollow_finder.__main__.Parser')
    @mock.patch('nofollow_finder.__main__.Processor')
    @mock.patch('nofollow_finder.__main__.log')
    def test_main_default_verbose(
            self, p_log, p_processor, p_parser, p_downloader, p_output,
            p_input):
        main.main(
            'in_file.csv', ['example.com'], 'log_file.log', 'out_file.csv',
            overwrite=True, header=False, verbosity=4, redirect=True,
            timeout=2, mode=None, settings_file=False,
        )
        p_input.assert_called_once_with('in_file.csv')
        p_output.assert_called_once_with(
            'out_file.csv', ['example.com'], True, False)
        p_downloader.assert_called_once_with(follow_redirects=True, timeout=2)
        p_parser.assert_called_once_with(['example.com'])
        p_processor.assert_called_once_with(
            p_input.return_value,
            p_downloader.return_value,
            p_parser.return_value,
            p_output.return_value,
        )
        p_processor.return_value.process.assert_called_once_with()
        p_log.debug.assert_called()
        p_log.error.assert_called_once_with('Sample error message')
        p_log.critical.assert_called_once_with('Sample critical message')
