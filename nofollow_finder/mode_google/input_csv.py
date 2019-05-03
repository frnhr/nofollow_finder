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
from .google_search import GoogleSearch


log = logging.getLogger(__name__)


class GoogleInputCSV(WebSearchInputCSV):

    def get_web_search(self):
        return GoogleSearch(settings.GOOGLE_API_KEY, settings.GOOGLE_API_CX)

    def get_url(self, result):
        return result['link']
