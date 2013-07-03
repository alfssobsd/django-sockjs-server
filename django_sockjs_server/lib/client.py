import logging
import time
import json
import pika
from pika.exceptions import ChannelClosed, AMQPConnectionError
from django_sockjs_server.lib.config import SockJSSereverSettings


class SockJsServerClient(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = SockJSSereverSettings()
        self.connected = False
        self.retry_count = 0

        self._connect()

    def _connect(self):
        cred = pika.PlainCredentials(self.config.rabbitmq_user, self.config.rabbitmq_password)
        param = pika.ConnectionParameters(
            host=self.config.rabbitmq_host,
            port=self.config.rabbitmq_port,
            virtual_host=self.config.rabbitmq_vhost,
            credentials=cred
        )
        self.connection = pika.BlockingConnection(param)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.config.rabbitmq_exhange_name,
                                      exchange_type=self.config.rabbitmq_exchange_type)
        self.connected = True
        self.retry_count = 0

    def _disconnect(self):
        self.connected = False
        self.connection.disconnect()

    def publish_message(self, message):
        try:
            if not self.connected:
                self._connect()
            self.channel.basic_publish(self.config.rabbitmq_exhange_name, routing_key='',  body=json.dumps(message))
        except (ChannelClosed, AMQPConnectionError):
            if self.connected:
                self._disconnect()
            if self.retry_count < 4:
                self.retry_count += 1
                #wait 100 ms
                time.sleep(100 / 1000000.0)
                self.publish_message(message)
