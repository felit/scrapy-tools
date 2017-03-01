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
        },'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Host': 'www.dianping.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36',
        }
    }

    def parse(self, response):
        item = DianpingItem()
        item['title'] = 'dian ping'
        yield item