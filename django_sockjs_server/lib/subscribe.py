import json
import logging
import time
import datetime
import hashlib
import random
from django_sockjs_server.lib.token import Token
from django_sockjs_server.lib.redis_client import redis_client

class Subscribe(object):

    def __init__(self, connection):
        u'''
            connection: django_sockjs_server.lib.sockjs_handler.SockJSConnection
        '''
        self.conn = connection
        self.logger = logging.getLogger(__name__)
        self.redis = redis_client

    def get_host(self):
        return self.conn.sockjs_server.queue

    def _compat_transform(self, json_obj):
        data = json_obj['data']
        if 'room' not in data and 'channel' in data:
            data['room'] = data['channel']

    def add(self, data):
        try:
            json_obj = json.loads(data)
            token = Token()
            self._compat_transform(json_obj)
            if token.get_data(json_obj['token'], json_obj['data']['room']):
                #uid = self._generate_id(json_obj)
                host = self.get_host()
                room = json_obj['data']['room']
                uid = self.conn.id
                self.conn.sockjs_server.add_subscriber_room(
                    room, self.conn
                )
                self.logger.debug(
                    'django-sockjs-server (Subscribe): Subscribe to channel %s' % room
                )
                self.redis.lpush(
                    room,
                    json.dumps({'host': host, 'id': uid})
                )
        except (KeyError, TypeError):
            pass

    def remove(self):
        host = self.get_host()
        uid = self.conn.id
        for room in self.conn.sockjs_server.subscription_dict[uid]:
            self.redis.lrem(
                room,
                0,
                json.dumps({'id': uid, 'host': host})
            )
        self.conn.sockjs_server.remove_subscriber(uid)
        self.logger.debug(
            'django-sockjs-server(Subscirbe):Unsubscrbe from connection %s' % uid
        )
