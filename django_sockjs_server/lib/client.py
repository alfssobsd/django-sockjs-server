import redis
import logging
import time
import json
import pika
from pika.exceptions import ChannelClosed, AMQPConnectionError
from django.core.serializers.json import DjangoJSONEncoder
from django_sockjs_server.lib.config import SockJSServerSettings
from django_sockjs_server.lib.redis_client import redis_client


class SockJsServerClient(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = SockJSServerSettings()
        self.connected = False
        self.retry_count = 0
        self.redis = redis_client

    def _connect(self, is_retry=False):
        cred = pika.PlainCredentials(self.config.rabbitmq_user, self.config.rabbitmq_password)
        param = pika.ConnectionParameters(
            host=self.config.rabbitmq_host,
            port=self.config.rabbitmq_port,
            virtual_host=self.config.rabbitmq_vhost,
            credentials=cred
        )
        self.connection = pika.BlockingConnection(param)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.config.rabbitmq_exchange_name,
                                      exchange_type=self.config.rabbitmq_exchange_type)


        self.connected = True
        if not is_retry:
            self.retry_count = 0

    def _disconnect(self):
        self.connected = False
        self.connection.disconnect()

    def publish_message_old(self, message):
        room = message.pop('channel')
        connections = self.get_connections(room)
        for conn in connections:
            submessage = message.copy()
            submessage['host'] = conn['host']
            submessage['uid'] = conn['id']
            submessage['room'] = room
            self.channel.basic_publish(
                self.config.rabbitmq_exchange_name,
                routing_key=submessage['host'],
                body=json.dumps(submessage, cls=DjangoJSONEncoder)
            )


    def publish_message(self, message, is_retry=False):
        try:
            if not self.connected:
                self._connect(is_retry)
            self.logger.debug("PUBLISH: %s" % message)
            # backward compatibility
            if 'channel' in message:
                self.publish_message_old(message)
            else:
                routing_key = message['host']
                self.channel.basic_publish(self.config.rabbitmq_exchange_name,
                                           routing_key=routing_key,
                                           body=json.dumps(message, cls=DjangoJSONEncoder))
        except (ChannelClosed, AMQPConnectionError):
            if self.connected:
                self._disconnect()
            if self.retry_count < 4:
                self.retry_count += 1
                #wait 100 ms
                time.sleep(100 / 1000000.0)
                self.publish_message(message, True)


    def get_connections(self, room):
        if not self.connected:
            self._connect()
            parsed_connections = []
        connections = self.redis.lrange(room, 0, -1)
        res = []
        for i in connections:
            try:
                res.append(json.loads(i))
            except ValueError:
                pass
        return res
