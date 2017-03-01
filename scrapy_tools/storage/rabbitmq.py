# -*- coding:utf-8 -*-
from scrapy import signals
import traceback
from scrapy.exceptions import NotConfigured
import logging

logger = logging.getLogger(__name__)


class RabbitMQSignal():
    def __init__(self, crawler):
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def item_scraped(self, item, spider):
        print item


