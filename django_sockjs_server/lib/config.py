from django.conf import settings

__author__ = 'Sergey Kravchuk'

class SockJSSereverSettings(object):

    def __init__(self):
        conf = getattr(settings, 'DJANGO_SOCKJS_SERVER', None)
        if not conf:
            raise Exception('django-sockjs-server error! No settings.')

        self.rabbitmq_user = conf.get('rabbitmq_user', 'guest')
        self.rabbitmq_password = conf.get('rabbitmq_password', 'guest')
        self.rabbitmq_host = conf.get('rabbitmq_server_host', 'localhost')
        self.rabbitmq_port = int(conf.get('rabbitmq_server_port', 5672))
        self.rabbitmq_vhost = conf.get('rabbitmq_server_vhost', '/')
        self.rabbitmq_exhange_name = conf.get('rabbitmq_exhange_name', 'sockjs')
        self.rabbitmq_exchange_type = conf.get('rabbitmq_exchange_type', 'fanout')

        self.listen_addr = conf.get('listen_addr', '0.0.0.0')
        self.listen_port = int(conf.get('listen_port', 8083))
        self.listen_location = conf.get('listen_location', '/ws')
        self.secret_key = conf.get('secret_key', 'not_set_secret_key')
        self.sockjs_url = conf.get('sockjs_url', 'http://localhost:8083/ws')

        self.router_settings = conf.get('router_settings', dict())
