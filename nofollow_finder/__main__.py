"""
nofollow_finder {version}

Usage:
  nofollow_finder -i <input_csv> -d <domains> [options]
  nofollow_finder (-v | --version)
  nofollow_finder (-h | --help)

Options:
  -i --input=<input_csv>  CSV file with URLs on the first column. Required.
  -d --domains=<domains>  List of domains, separated by commas. Required.
  -o --out=<out_file>     Output CSV file: "-"=stdout [default: out.csv]
  -l --log=<log_file>     Log file [default: nofollow_finder.log]
  -V --verbosity=<V>      Log verbosity: 0-4 [default: 3].
                          0=silent, 1=error, 2=warning, 3=info, 4=debug
  -R --redirect=<R>       Follow HTTP redirects: 0,1 [default: 1]
  -t --timeout=<T>        Timeout for HTTP traffic: 1-{MT}, 0=none [default: 7]
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

import docopt

from nofollow_finder.downloader import Downloader
from nofollow_finder.input_csv import InputCSV
from nofollow_finder.output_csv import OutputCSV
from nofollow_finder.parser import Parser
from nofollow_finder.processor import Processor


MAX_TIMEOUT = 60  # seconds
VERSION = ('0', '0', '1')
__version__ = '.'.join(VERSION)


__doc__ = __doc__.format(
    version=__version__,
    MT=MAX_TIMEOUT,
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
    if args_['--redirect'] not in ('0', '1'):
        raise docopt.DocoptExit('Redirect not one of: 0, 1')
    return bool(int(args_['--redirect']))


def validate_domains(args_):
    domains = filter(None, args_['--domains'].split(','))
    return domains


def validate_log_file(args_):
    log_file = args_['--log']
    if log_file == '-':
        log_file = None
    return log_file


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


def main(in_file, domains, log_file, out_file, verbosity, redirect, timeout):
    _configure_log(log_file, verbosity)
    log.debug('start')
    if verbosity == 4:
        log.debug("Sample debug message")
        log.info("Sample info message")
        log.warning("Sample warning message")
        log.error("Sample error message")
        log.critical("Sample critical message")
    input_csv = InputCSV(in_file)
    output_csv = OutputCSV(out_file)
    downloader = Downloader(follow_redirects=redirect, timeout=timeout)
    parser = Parser(domains)
    processor = Processor(input_csv, downloader, parser, output_csv)
    processor.process()
    log.debug('done')


def run_from_cli():
    args = docopt.docopt(__doc__, version=__doc__.strip().splitlines()[0])
    arguments_ = docopt.Dict({
        'in_file': args['--input'],
        'domains': validate_domains(args),
        'log_file': validate_log_file(args),
        'out_file': args['--out'],
        'verbosity': validate_verbosity(args),
        'redirect': validate_redirect(args),
        'timeout': validate_timeout(args),
    })
    main(**arguments_)


if __name__ == '__main__':
    run_from_cli()
