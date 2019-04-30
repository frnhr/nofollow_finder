# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..output_csv import OutputCSV


class GoogleOutputCSV(OutputCSV):
    FIXED_HEADER = ('URL', 'query', 'HTTP response code',)
    FIXED_COLS = 'url query http_response'
