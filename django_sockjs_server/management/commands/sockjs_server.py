import logging
import tornado
from django.core.management.base import BaseCommand
from django_sockjs_server.lib.config import SockJSSereverSettings
from django_sockjs_server.lib.sockjs_handler import SockJSRouter, SockJSConnection

class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info('start django-sockjs-server')
        self.config = SockJSSereverSettings()

        io_loop = tornado.ioloop.IOLoop.instance()

        router = SockJSRouter(
            SockJSConnection,
            self.config.listen_location)
        app = tornado.web.Application(router.urls)

        app.listen(self.config.listen_port, address=self.config.listen_addr)
        try:
            io_loop.start()
        except KeyboardInterrupt:
            pass