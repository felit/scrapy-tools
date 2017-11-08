# -*- coding:utf8 -*-
import pika

conn = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost",
                              port=5672,
                              virtual_host="/"))
channel = conn.channel()
exchange = "exchange-test"
queue = "queue-test"
result = channel.queue_declare(queue=queue, durable=True, exclusive=False)
# pub/sub模式
channel.exchange_declare(durable=True, exchange=exchange, type='fanout', )
channel.queue_bind(exchange=exchange, queue=result.method.queue, routing_key='', )

import datetime
def cons(ch, method, properties, body):
    print ch
    print body
    print datetime.datetime.now()


channel.basic_consume(cons, queue=queue, no_ack=False)
channel.start_consuming()
