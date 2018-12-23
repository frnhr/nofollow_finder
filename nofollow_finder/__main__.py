#!/usr/bin/env python
# coding=utf-8

"""
nofollow_finder {version}

Usage:
  nofollow_finder -d <domains> [options]
  nofollow_finder [-i <input_csv>] -d <domains> [-o <out_file> [-a | -f]] \
[options]
  nofollow_finder (-v | --version)
  nofollow_finder (-h | --help)

Options:
  -i --input=<input_csv>  CSV file with URLs on the first column. Required.
  -d --domains=<domains>  List of domains, separated by commas. Required.
  -o --out=<out_file>     Output CSV file. Default: stdout.
  -a --append             Append to existing CSV file.
  -f --force              Overwrite existing CSV file.
                          "-a" and "-f" are ignored when file does not exist.
  -l --log=<log_file>     Log file. Default: stderr
  -V --verbosity=<V>      Log verbosity: 0-4 [default: 3]
                          0=silent, 1=error, 2=warning, 3=info, 4=debug
  -L --nofollow           Do not follow HTTP redirects (301, 302, etc.).
  -t --timeout=<T>        Timeout for HTTP traffic: 1-{mt}, 0=none [default: 7]
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
from nofollow_finder.output_csv import OutputCSV
from nofollow_finder.parser import Parser
from nofollow_finder.processor import Processor

MAX_TIMEOUT = 30  # seconds
DEFAULT_LOFG = 'nofollow_finder.log'
__version__ = '0.0.1'
VERSION = tuple(__version__.split('.'))

__doc__ = __doc__.format(
    version=__version__,
    mt=MAX_TIMEOUT,
    default_log=DEFAULT_LOFG,
)

log = logging.getLogger(__name__)

LOG_FORMAT = (
    '%(levelname)-8s  %(asctime)s  %(process)-5d  %(name)-26s  %(message)s')


def _configure_log(log_file, verbosity):
    level = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }[verbosity]
    logging.basicConfig(filename=log_file, level=level, format=LOG_FORMAT)


def validate_verbosity(args_):
    if args_['--verbosity'] not in ('0', '1', '2', '3', '4'):
        raise docopt.DocoptExit('Verbosity not one of: 0, 1, 2, 3, 4')
    return int(args_['--verbosity'])


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
    if timeout >= MAX_TIMEOUT:
        raise docopt.DocoptExit(
            'Timeout has to be {} or less.'.format(MAX_TIMEOUT))
    return timeout


def validate_overwrite(args_):
    append = args_['--append']
    force = args_['--force']
    out_file = args_['--out']
    is_stdout = out_file is None
    exists = (not is_stdout) and os.path.isfile(out_file)
    if exists and not append and not force:
        raise docopt.DocoptExit(
            'Output file already exists. Overwrite: "-f" or append: "-a"')
    return not append


def validate_input(args_):
    in_file = args_['--input']
    if in_file is None:
        return in_file
    exists = os.path.isfile(in_file)
    if not exists:
        raise docopt.DocoptExit(
            'Input file does not exist.')
    return in_file


def validate_output(args_):
    out_file = args_['--out']
    return out_file


def main(in_file, domains, log_file, out_file, overwrite, verbosity, redirect,
         timeout):
    _configure_log(log_file, verbosity)
    log.debug('start')
    if verbosity == 4:
        log.debug("Sample debug message")
        log.info("Sample info message")
        log.warning("Sample warning message")
        log.error("Sample error message")
        log.critical("Sample critical message")
    input_csv = InputCSV(in_file)
    output_csv = OutputCSV(out_file, overwrite)
    downloader = Downloader(follow_redirects=redirect, timeout=timeout)
    parser = Parser(domains)
    processor = Processor(input_csv, downloader, parser, output_csv)
    processor.process()
    log.debug('done')


def run_from_cli():
    args = docopt.docopt(__doc__, version=__doc__.strip().splitlines()[0])
    arguments_ = docopt.Dict({
        'in_file': validate_input(args),
        'domains': validate_domains(args),
        'log_file': validate_log_file(args),
        'out_file': validate_output(args),
        'overwrite': validate_overwrite(args),
        'verbosity': validate_verbosity(args),
        'redirect': validate_redirect(args),
        'timeout': validate_timeout(args),
    })
    main(**arguments_)


if __name__ == '__main__':
    run_from_cli()
