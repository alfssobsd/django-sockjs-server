import datetime
import time
import redis
import logging
import functools
from django_sockjs_server.lib.config import SockJSServerSettings

def reconnect_wrapper(func):
    @functools.wraps(func)
    def myfunc(self, *args, **kwargs):
        while True:
            try:
                return func(self, *args, **kwargs)
            except redis.ConnectionError:
                self.logger.info('django-sockjs-server(RedisClient): error connect, wait 5 sec')
                self.connect()
                time.sleep(5)
    return myfunc


class RedisClient(object):
    def __init__(self):
        self.config = SockJSServerSettings()
        self.connect_tries = 0
        self.connecting = False
        self.last_reconnect = None
        self.connect()
        self.logger = logging.getLogger(__name__)

    def get_uptime(self):
        if self.last_reconnect:
            return (datetime.datetime.now() - self.last_reconnect).seconds

    def connect(self):
        if not self.connecting:
            self.connecting = True
            self.connect_tries += 1
            while self.connecting:
                try:
                    self.redis = redis.StrictRedis(
                        host=self.config.redis_host,
                        port=self.config.redis_port,
                        db=self.config.redis_db,
                        password=self.config.redis_password
                    )
                except redis.ConnectionError:
                    self.logger.info('django-sockjs-server(RedisClient): error connect, wait 5 sec')
                    time.sleep(5)
                else:
                    self.connecting = False
                    self.last_reconnect = datetime.datetime.now()
        else:
            self.logger.info('django-sockjs-server(RedisClient): already connected')


    def get_real_key(self, key):
        return self.config.redis_prefix + key

    def log(self, *args):
        formatters = "%s " * len(args)
        format_string = "django-sockjs-server(RedisClient): " + formatters
        self.logger.debug(format_string % args)
        
    @reconnect_wrapper
    def lpush(self, key, *args, **kwargs):
        self.log('lpush', key, args, kwargs)
        return self.redis.lpush(self.get_real_key(key), *args, **kwargs)
        
    @reconnect_wrapper
    def lrange(self, key, *args, **kwargs):
        self.log('lrange', key, args, kwargs)
        return self.redis.lrange(self.get_real_key(key), *args, **kwargs)

    @reconnect_wrapper
    def lrem(self, key, num, value):
        self.log('lrem', key, num, value)
        return self.redis.lrem(self.get_real_key(key), num, value)


redis_client = RedisClient()
