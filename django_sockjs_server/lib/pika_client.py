from collections import defaultdict
import json
import logging
from django.conf import settings
from django.utils.timezone import now
import pika
from pika.adapters.tornado_connection import TornadoConnection
from pika.exceptions import AMQPConnectionError
import time
from django_sockjs_server.lib.config import SockJSSereverSettings


class PikaClient(object):
    def __init__(self, io_loop):
        self.logger = logging.getLogger(__name__)
        self.logger.info('PikaClient: __init__')
        self.io_loop = io_loop

        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

        self.event_listeners_count = 0
        self.event_listeners = set()
        self.subscrib_channel = defaultdict(set)
        self.last_reconnect = now()
        self.uptime_start = now()



        self.config = SockJSSereverSettings()

    def connect(self):
        if self.connecting:
            self.logger.info('django-sockjs-server(PikaClient): Already connecting to RabbitMQ')
            return

        self.logger.info('django-sockjs-server(PikaClient): Connecting to RabbitMQ')
        self.connecting = True

        cred = pika.PlainCredentials(self.config.rabbitmq_user, self.config.rabbitmq_password)
        param = pika.ConnectionParameters(
            host=self.config.rabbitmq_host,
            port=self.config.rabbitmq_port,
            virtual_host=self.config.rabbitmq_vhost,
            credentials=cred
        )

        try:
            self.connection = TornadoConnection(param,
                                                on_open_callback=self.on_connected)
            self.connection.add_on_close_callback(self.on_closed)
        except AMQPConnectionError:
            self.logger.info('django-sockjs-server(PikaClient): error connect, wait 5 sec')
            time.sleep(5)
            self.reconnect()

        self.last_reconnect = now()

    def on_connected(self, connection):
        self.logger.info('django-sockjs-server(PikaClient): connected to RabbitMQ')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.info('django-sockjs-server(PikaClient): Channel open, Declaring exchange')
        self.channel = channel
        self.channel.exchange_declare(exchange=self.config.rabbitmq_exhange_name,
                                      exchange_type=self.config.rabbitmq_exchange_type)
        self.channel.queue_declare(exclusive=False, auto_delete=True, callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        self.logger.info('django-sockjs-server(PikaClient): queue bind')
        self.channel.queue_bind(callback=None, exchange=self.config.rabbitmq_exhange_name, queue=frame.method.queue)
        self.channel.basic_consume(self.handle_delivery, queue=frame.method.queue, no_ack=True)

    def handle_delivery(self, channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        self.notify_listeners(body)

    def on_closed(self, connection, error_code, error_message):
        self.logger.info('django-sockjs-server(PikaClient): rabbit connection closed, wait 5 seconds')
        connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        self.connecting = False
        self.logger.info('django-sockjs-server(PikaClient): reconnect')
        self.connect()

    def notify_listeners(self, event_json):
        event_obj = json.loads(event_json)

        self.logger.debug('django-sockjs-server(PikaClient): get new data  = %s ' % event_obj)
        try:
            if len(self.subscrib_channel[event_obj['channel']]) > 0:
                for client in self.subscrib_channel[event_obj['channel']]:
                    self.logger.debug('django-sockjs-server(PikaClient): send message channel = %s ' % event_obj['channel'])
                    client.broadcast(self.subscrib_channel[event_obj['channel']], event_json)
                    break
        except KeyError:
            pass

    def add_event_listener(self, listener):
        self.event_listeners.add(listener)
        self.event_listeners_count += 1
        self.logger.debug('django-sockjs-server(PikaClient): listener %s added' % repr(listener))

    def remove_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            self.event_listeners_count -= 1
            self.logger.debug('django-sockjs-server(PikaClient): listener %s removed' % repr(listener))
        except KeyError:
            pass

    def add_subscriber_channel(self, chanel, client):
        self.subscrib_channel[chanel].add(client)
        self.logger.debug('django-sockjs-server(PikaClient): listener %s add to channel %s' % (repr(client), chanel))

    def remove_subscriber_channel(self, chanel, client):
        try:
            self.subscrib_channel[chanel].remove(client)
            self.logger.debug('django-sockjs-server(PikaClient): listener %s remove from channel %s' % (repr(client),
                              chanel))
        except KeyError:
            pass

    def get_event_listeners_count(self):
        return self.event_listeners_count

    def get_subscribe_channel_count(self):
        return len(self.subscrib_channel.keys())

    def get_subscribe_channels(self):
        return self.subscrib_channel.keys()

    def get_last_reconnect(self):
        return self.last_reconnect

    def get_uptime(self):
        return (now() - self.uptime_start).seconds