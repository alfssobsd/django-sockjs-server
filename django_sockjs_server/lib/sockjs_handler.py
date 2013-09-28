import logging
from django.utils.timezone import now
import sockjs.tornado
from tornado.web import RequestHandler
from django_sockjs_server.lib.memory_stats import MemoryStats
from django_sockjs_server.lib.pika_client import PikaClient
from django_sockjs_server.lib.subscribe import Subscribe

class SockJSConnection(sockjs.tornado.SockJSConnection):

    pika_client = None  # should be initialized by router

    def __init__(self, *args, **kw):
        self.subscribe_list = set()
        self.subscribe = Subscribe(self)
        self.logger = logging.getLogger(__name__)
        super(SockJSConnection, self).__init__(*args, **kw)

    def on_open(self, info):
        self.pika_client.add_event_listener(self)

    def on_close(self):
        self.subscribe.remove()
        self.pika_client.remove_event_listener(self)

    def on_message(self, message):
        self.logger.debug('Get message %s' % message)
        self.subscribe.add(message)

class StatsHandler(RequestHandler):
    def initialize(self, pika_client):
        self.pika_client = pika_client
        self.memory_stats = MemoryStats()

    def get(self, type_stats='default'):
        self.clear()
        self.set_header("Content-Type", "text/plain")
        self.set_status(200)
        if type_stats == 'debug':
            self.finish("uptime_seconds: " + str(self.pika_client.get_uptime()) +
                        "\n memory_use_byte: " + str(int(self.memory_stats.memory())) +
                        "\n memory_resident_use_byte: " + str(int(self.memory_stats.resident())) +
                        "\n memory_stack_size_byte: " + str(int(self.memory_stats.stacksize())) +
                        "\n last_rabbitmq_reconnect: " + str(self.pika_client.get_last_reconnect()) +
                        "\n connect_rabbitmq_time_seconds: " + str((now() - self.pika_client.get_last_reconnect()).seconds) +
                        "\n connects: " + str(self.pika_client.get_event_listeners_count()) +
                        "\n channel_count: " + str(len(self.pika_client.get_subscribe_channels())) +
                        "\n channels: " + str(self.pika_client.get_subscribe_channels()))
        else:
            self.finish("uptime_seconds: " + str(self.pika_client.get_uptime()) +
                        "\n memory_use_byte: " + str(int(self.memory_stats.memory())) +
                        "\n memory_resident_use_byte: " + str(int(self.memory_stats.resident())) +
                        "\n memory_stack_size_byte: " + str(int(self.memory_stats.stacksize())) +
                        "\n last_rabbitmq_reconnect: " + str(self.pika_client.get_last_reconnect()) +
                        "\n connect_rabbitmq_time_seconds: " + str((now() - self.pika_client.get_last_reconnect()).seconds) +
                        "\n connects: " + str(self.pika_client.get_event_listeners_count()) +
                        "\n channel_count: " + str(len(self.pika_client.get_subscribe_channels())))


class SockJSRouterPika(sockjs.tornado.SockJSRouter):
    def __init__(self, *args, **kw):
        super(SockJSRouterPika, self).__init__(*args, **kw)
        self._connection.pika_client = PikaClient(self.io_loop)
        self._connection.pika_client.connect()