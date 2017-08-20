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


class RabbitMQStore():
    """
      默认host: localhost
      queue: crawler
      exchange: exchange
      TODO 添加 依据item字段识别至不同的队列里面
    """

    def __init__(self,
                 crawler,
                 host='localhost',
                 queue='crawler',
                 exchange='exchange',
                 username=None,
                 password=None,
                 port=5672,
                 virtual_host="/"):
        self.host = host
        self.queue = queue
        self.exchange = exchange
        self.username = username
        self.password = password
        self.port = port
        self.virtual_host = virtual_host
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(self.spider_error, signal=signals.spider_error)
        self.saved_queue_key = "RABBITMQ_QUEUE_KEY"
        self.saved_exchange_key = "RABBITMQ_EXCHANGE_KEY"
        self.queue_declared = []

    @classmethod
    def from_settings(cls, crawler, settings):
        params = {
            'host': settings['RABBITMQ_SERVER'],
            'crawler': crawler
        }
        params['port'] = settings['RABBITMQ_PORT']
        params['queue'] = settings['RABBITMQ_QUEUE']
        params['exchange'] = settings['RABBITMQ_EXCHANGE']
        params['username'] = settings['RABBITMQ_USERNAME']
        params['password'] = settings['RABBITMQ_PASSWORD']
        params['virtual_host'] = settings['RABBITMQ_VIRTUAL_HOST']
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler, crawler.settings)

    def item_scraped(self, item, spider):
        map = {}
        queue = self.queue

        for key, val in item.items():
            if key == self.saved_exchange_key:
                exchange = val
            elif key == self.saved_queue_key:
                queue = val
            elif isinstance(val, datetime):
                map[key] = val.strftime('%Y-%m-%d %H:%M:%S')
            else:
                map[key] = val
        # 如果队列没有声明过 则声明队列
        if queue != self.queue and exchange is not None and queue not in self.queue_declared:
            self.declare(queue, exchange)
        """
            Traceback (most recent call last):
              File "/usr/local/lib/python2.7/dist-packages/twisted/internet/defer.py", line 150, in maybeDeferred
                result = f(*args, **kw)
              File "/usr/local/lib/python2.7/dist-packages/pydispatch/robustapply.py", line 55, in robustApply
                return receiver(*arguments, **named)
              File "build/bdist.linux-x86_64/egg/scrapy_tools/storage/rabbitmq.py", line 71, in item_scraped
              File "/usr/lib/python2.7/json/__init__.py", line 244, in dumps
                return _default_encoder.encode(obj)
              File "/usr/lib/python2.7/json/encoder.py", line 207, in encode
                chunks = self.iterencode(o, _one_shot=True)
              File "/usr/lib/python2.7/json/encoder.py", line 270, in iterencode
                return _iterencode(o, 0)
            UnicodeDecodeError: 'utf8' codec can't decode bytes in position 0-1: invalid continuation byte
        """
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=json.dumps(map),
                                   properties=pika.BasicProperties(delivery_mode=2, ))
        # print 'from rabbitmq signal:%s' % (json.dumps(map))

    def spider_opened(self, spider):
        if self.username is not None:
            user_pwd = pika.PlainCredentials(self.username, self.password)
            con = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host,
                                          port=self.port,
                                          credentials=user_pwd,
                                          virtual_host=self.virtual_host))
        else:
            con = pika.BlockingConnection(pika.ConnectionParameters(self.host, virtual_host=self.virtual_host))
        self.channel = con.channel()
        self.declare(self.queue, self.exchange)

    def declare(self, queue, exchange):
        """

        :param queue:
        :param exchange:
        :return:
        """
        result = self.channel.queue_declare(queue=queue, durable=True, exclusive=False)
        # pub/sub模式
        self.channel.exchange_declare(durable=True, exchange=exchange, type='fanout', )
        self.channel.queue_bind(exchange=exchange, queue=result.method.queue, routing_key='', )

    def spider_closed(self, spider, reason):
        if not self.channel.is_closed:
            self.channel.close()

    def spider_error(self, failure, response, spider):
        # if not self.channel.is_closed:
        # self.channel.close()
        pass


