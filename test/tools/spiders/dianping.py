# -*- coding: utf-8 -*-
import scrapy
from tools.items import DianpingItem

# from scrapy_tools.storage.rabbitmq import RabbitMQSignal
class DianpingSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["dianping.com"]
    start_urls = ['http://www.dianping.com/search/category/2/10/r2578']
    custom_settings = {
        'EXTENSIONS': {
            'scrapy_tools.storage.rabbitmq.RabbitMQSignal': 200
        },
    }

    def parse(self, response):
        item = DianpingItem()
        item['title'] = 'dian ping'

        pass
