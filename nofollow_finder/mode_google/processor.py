# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging

from ..processor import Processor, UrlData


log = logging.getLogger(__name__)


class GoogleProcessor(Processor):

    def make_url_data(self, link):
        return UrlData(
            domains=self.domains,
            url=link['url'],
            query=link['query'],
            http_response=0,
        )
