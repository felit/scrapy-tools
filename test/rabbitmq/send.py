# -*- coding:utf8 -*-
import pika, time

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
channel.basic_publish(exchange='',
                      routing_key=queue,
                      body="queue-test-content%s" % (time.time()),
                      properties=pika.BasicProperties(delivery_mode=2, ))
