# -*- coding:utf-8 -*-
from scrapy import signals
import traceback
from scrapy.exceptions import NotConfigured
import logging
import pika
import sys
import time
import json

logger = logging.getLogger(__name__)
from datetime import datetime


class RabbitMQSignal():
    def __init__(self, crawler, host='localhost', queue='crawler', exchange='exchange', username=None, password=None):
        self.host = host
        self.queue = queue
        self.exchange = exchange
        self.username = username
        self.password = password
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(self.spider_error, signal=signals.spider_error)

    @classmethod
    def from_settings(cls, crawler, settings):
        params = {
            'host': settings['RABBITMQ_SERVER'],
            'crawler': crawler
        }
        params['queue'] = settings['RABBITMQ_QUEUE']
        params['exchange'] = settings['RABBITMQ_EXCHANGE']
        params['username'] = settings['RABBITMQ_USERNAME']
        params['password'] = settings['RABBITMQ_PASSWORD']
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):

        return cls.from_settings(crawler, crawler.settings)

    def item_scraped(self, item, spider):
        map = {}
        for key, val in item.items():
            if isinstance(val, datetime):
                map[key] = val.strftime('%Y-%m-%d %H:%M:%S')
            else:
                map[key] = val
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   body=json.dumps(map),
                                   properties=pika.BasicProperties(delivery_mode=2, ))
        print 'from rabbitmq signal:%s' % (json.dumps(map))

    def spider_opened(self, spider):
        if self.username is not None:
            user_pwd = pika.PlainCredentials(self.username, self.password)
            con = pika.BlockingConnection(pika.ConnectionParameters(self.host, user_pwd))
        else:
            con = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = con.channel()
        result = self.channel.queue_declare(queue=self.queue, durable=True, exclusive=False)
        # pub/sub模式
        self.channel.exchange_declare(durable=True, exchange=self.exchange, type='fanout', )
        self.channel.queue_bind(exchange=self.exchange, queue=result.method.queue, routing_key='', )

    def spider_closed(self, spider, reason):
        self.channel.close()

    def spider_error(self, failure, response, spider):
        self.channel.close()


