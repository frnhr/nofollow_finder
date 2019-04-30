#!/usr/bin/env python
# coding=utf-8

"""
nofollow_finder {version}

Usage:
  nofollow_finder -d <domains> [options]
  nofollow_finder [-i <input_csv>] -d <domains> [-o <out_file> [-a | -f]] \
[options]
  nofollow_finder --google [-c <count>] [-i <input_csv>] -d <domains> \
[-o <out_file> [-a | -f]] [options]
  nofollow_finder test
  nofollow_finder (-v | --version)
  nofollow_finder (-h | --help)

Options:
  -i --input=<input_csv>  CSV file with URLs or Google query terms on
                          the first column. Required.
                          `+` has a special meaning, standing in for hardcoded
                          defaults.
  -d --domains=<domains>  List of domains, separated by commas. Required.
  -o --out=<out_file>     Output CSV file. Default: stdout.
  -a --append             Append to existing CSV file.
  -f --force              Overwrite existing CSV file.
                          "-a" and "-f" are ignored when file does not exist.
  -g --google             Run in "Google" mode. First column in the CSV input
                          file will be treated as query terms.
  -c --count=<count>      Each term will be searched for on Google, and top
                          <count> results will be processed. [default: {COUNT}]
  -e --header             Force header row creation in CSV output.
  -n --noheader           Prevent header row creation in CSV output.
                          Default: add headers only when creating a new file.
  -l --log=<log_file>     Log file. Default: stderr
  -s --settings=<settings_file>
                          Path to the settings file. Can be a list of \
comma-separated paths. First one that exists will be used. \
[default: .nofollowfinderrc,~/.nofollowfinderrc]
  -V --verbosity=<V>      Log verbosity: 0-4 [default: 3]
                          0=silent, 1=error, 2=warning, 3=info, 4=debug
  -L --nofollow           Do not follow HTTP redirects (301, 302, etc.).
  -t --timeout=<T>        Timeout for HTTP traffic: 1-{m}, 0=none [default: 60]
  -v --version            Show program name and version.
  -h --help               Show this help text and exit.
"""
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import os

import docopt

from nofollow_finder.downloader import Downloader
from nofollow_finder.input_csv import InputCSV
from nofollow_finder.mode_google import (
    GoogleInputCSV,
    GoogleOutputCSV,
    GoogleProcessor,
)
from nofollow_finder.output_csv import OutputCSV
from nofollow_finder.parser import Parser
from nofollow_finder.processor import Processor
from nofollow_finder.settings import settings

_minutes_ = 60

MAX_TIMEOUT = 5 * _minutes_
DEFAULT_LOFG = 'nofollow_finder.log'
__version__ = '1.3.1'
VERSION = tuple(__version__.split('.'))
DEFAULT_COUNT = 12

__doc__ = __doc__.format(
    version=__version__,
    m=MAX_TIMEOUT,
    default_log=DEFAULT_LOFG,
    COUNT=DEFAULT_COUNT,
)

log = logging.getLogger(__name__)

LOG_FORMAT = (
    '%(levelname)-8s  %(asctime)s  %(process)-5d  %(name)-43s  %(message)s')


def _configure_log(log_file, verbosity):
    level = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }[verbosity]
    logging.basicConfig(filename=log_file, level=level, format=LOG_FORMAT)


def _output_args(args_):
    append = args_['--append']
    force = args_['--force']
    out_file = args_['--out']
    is_stdout = out_file is None
    exists = (not is_stdout) and os.path.isfile(out_file)
    return(
        exists,  # it is a file and it already exists (False for strout)
        is_stdout,  # it is stdout and not a file
        append,  # provided `-a` or `--append`
        force,  # provided `-f` or `--force`
    )


def validate_verbosity(args_):
    if args_['--verbosity'] not in ('0', '1', '2', '3', '4'):
        raise docopt.DocoptExit('Verbosity not one of: 0, 1, 2, 3, 4')
    return int(args_['--verbosity'])


def validate_settings(args_):
    return args_['--settings']


def validate_redirect(args_):
    return not args_['--nofollow']


def validate_domains(args_):
    domains = filter(None, args_['--domains'].split(','))
    return domains


def validate_log_file(args_):
    return args_['--log']


def validate_timeout(args_):
    timeout = args_['--timeout']
    try:
        timeout = int(timeout)
    except ValueError:
        raise docopt.DocoptExit('Timeout has to be a number.')
    if timeout < 0:
        raise docopt.DocoptExit('Timeout has to be 0 or greater.')
    if timeout > MAX_TIMEOUT:
        raise docopt.DocoptExit(
            'Timeout has to be {} or less.'.format(MAX_TIMEOUT))
    return timeout


def validate_overwrite(args_):
    exists, is_stdout, append, force = _output_args(args_)
    if exists and not append and not force:
        raise docopt.DocoptExit(
            'Output file already exists. Overwrite: "-f" or append: "-a"')
    return not append


def validate_input(args_):
    in_file = args_['--input']
    if in_file is None:
        return in_file
    if in_file == '+' and validate_mode(args_) == 'google':
        return in_file
    exists = os.path.isfile(in_file)
    if not exists:
        raise docopt.DocoptExit(
            'Input file does not exist.')
    return in_file


def validate_output(args_):
    out_file = args_['--out']
    return out_file


def validate_header(args_):
    if args_['--header'] and args_['--noheader']:
        raise docopt.DocoptExit('Specify either -e or -n but not both.')
    exists, is_stdout, append, force = _output_args(args_)
    is_file = not is_stdout
    actually_appending = exists and append
    header = is_file and not actually_appending
    if args_['--header']:
        header = True
    if args_['--noheader']:
        header = False
    return header


def validate_mode(args_):
    if args_['--google']:
        return 'google'
    return None


def validate_kwargs(args_):
    if validate_mode(args_) == 'google':
        return {
            'count': int(args_['--count'] or DEFAULT_COUNT),
        }
    return {}


def main(in_file, domains, log_file, out_file, overwrite, header, verbosity,
         redirect, timeout, settings_file, mode, **kwargs):
    _configure_log(log_file, verbosity)
    log.debug('start')
    if verbosity == 4:
        log.debug("Sample debug message")
        log.info("Sample info message")
        log.warning("Sample warning message")
        log.error("Sample error message")
        log.critical("Sample critical message")
    settings.load(settings_file)

    downloader = Downloader(follow_redirects=redirect, timeout=timeout)
    parser = Parser(domains)
    if mode == 'google':
        input_csv = GoogleInputCSV(in_file, kwargs['count'])
        output_csv = GoogleOutputCSV(out_file, domains, overwrite, header)
        processor = GoogleProcessor(input_csv, downloader, parser, output_csv)
    else:
        input_csv = InputCSV(in_file)
        output_csv = OutputCSV(out_file, domains, overwrite, header)
        processor = Processor(input_csv, downloader, parser, output_csv)
    processor.process()
    log.debug('done')


def run_from_cli():
    args = docopt.docopt(__doc__, version=__doc__.strip().splitlines()[0])
    if args['test']:  # pragma no cover
        import unittest
        path = os.path.join(os.path.dirname(__file__), 'tests')
        suite = unittest.TestLoader().discover(path)
        runner = unittest.TextTestRunner()
        return runner.run(suite)
    arguments_ = docopt.Dict({
        'in_file': validate_input(args),
        'domains': validate_domains(args),
        'log_file': validate_log_file(args),
        'out_file': validate_output(args),
        'overwrite': validate_overwrite(args),
        'verbosity': validate_verbosity(args),
        'redirect': validate_redirect(args),
        'timeout': validate_timeout(args),
        'header': validate_header(args),
        'settings_file': validate_settings(args),
        'mode': validate_mode(args),
    })
    arguments_.update(**validate_kwargs(args))
    main(**arguments_)


if __name__ == '__main__':  # pragma no cover
    run_from_cli()
