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


class WebSearchProcessor(Processor):

    def make_url_data(self, link):
        return UrlData(
            domains=self.domains,
            url=link['url'],
            query=link['query'],
            engine=link['engine'],
            http_response=0,
        )
