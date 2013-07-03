import logging
import sockjs.tornado
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

class SockJSRouter(sockjs.tornado.SockJSRouter):
    def __init__(self, *args, **kw):
        super(SockJSRouter, self).__init__(*args, **kw)
        self._connection.pika_client = PikaClient(self.io_loop)
        self._connection.pika_client.connect()