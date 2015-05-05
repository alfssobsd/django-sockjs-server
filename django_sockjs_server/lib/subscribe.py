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
        


    def _generate_id(self, json_obj):
        now = datetime.datetime.utcnow()
        seconds = time.mktime(now.timetuple()) + now.microsecond / 1e6
        connection_id = hashlib.md5(
            u'%s %s %s' % (
                json_obj['token'],
                json_obj['data']['channel'],
                seconds
        )).hexdigest()
        return connection_id


    def get_host(self):
        return self.conn.sockjs_server.queue

    def add(self, data):
        try:
            json_obj = json.loads(data)
            token = Token()
            if token.get_data(json_obj['token'], json_obj['data']['channel']):
                uid = self._generate_id(json_obj)
                host = self.get_host()
                room = json_obj['data']['channel']
                self.logger.debug('django-sockjs-server:Subscrbe to channel %s' % json_obj['data']['channel'])

                self.redis.lpush(
                    json_obj['data']['channel'],
                    json.dumps({'host': host, 'id': uid})
                )

                self.conn.subscribe_list.add(uid)
                self.conn.sockjs_server.add_subscriber_room(
                    uid, room, self.conn
                )

        except (KeyError, TypeError):
            pass

    def remove(self):
        host = self.get_host()
        for uid in self.conn.subscribe_list:
            self.redis.lrem(
                self.conn.sockjs_server.subscrib_connection[uid]['room'],
                0,
                json.dumps({'id': uid, 'host': host})
            )
            self.conn.sockjs_server.remove_subscriber_room(uid, self.conn)
        self.conn.subscribe_list = []
