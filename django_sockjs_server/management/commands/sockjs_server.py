import logging
import tornado
from django.core.management.base import BaseCommand
from django_sockjs_server.lib.config import SockJSServerSettings
from django_sockjs_server.lib.sockjs_handler import SockJSRouterPika, SockJSConnection, StatsHandler


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info('start django-sockjs-server')
        self.config = SockJSServerSettings()

        io_loop = tornado.ioloop.IOLoop.instance()

        router = SockJSRouterPika(
            SockJSConnection,
            self.config.listen_location,
            user_settings=self.config.router_settings)
        app = tornado.web.Application([(r"/stats/(.*)", StatsHandler, dict(sockjs_server=router._connection.sockjs_server))] +
                                      router.urls)


        app.listen(
            self.config.listen_port, 
            address=self.config.listen_addr
        )
        try:
            io_loop.start()
        except KeyboardInterrupt:
            pass
