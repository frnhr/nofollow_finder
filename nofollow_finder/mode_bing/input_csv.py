# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging

from ..mode_web_search.input_csv import WebSearchInputCSV
from ..settings import settings
from .bing_search import BingSearch


log = logging.getLogger(__name__)


class BingInputCSV(WebSearchInputCSV):

    def get_web_search(self):
        return BingSearch(settings.BING_API_KEY)
