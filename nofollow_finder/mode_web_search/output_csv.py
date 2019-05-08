# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from ..output_csv import OutputCSV


class WebSearchOutputCSV(OutputCSV):
    FIXED_HEADER = ('URL', 'query', 'engine', 'HTTP response code',)
    FIXED_COLS = 'url query engine http_response'
