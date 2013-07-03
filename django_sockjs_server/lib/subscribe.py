import json
import logging
from django_sockjs_server.lib.token import Token

class Subscribe(object):

    def __init__(self, connection):
        self.conn = connection
        self.logger = logging.getLogger(__name__)

    def add(self, data):
        try:
            json_obj = json.loads(data)
            token = Token()
            if token.get_data(json_obj['token'], json_obj['data']['channel']):
                self.logger.debug('django-sockjs-server:Subscrbe to channel %s' % json_obj['data']['channel'])
                self.conn.subscribe_list.add(json_obj['data']['channel'])
                self.conn.pika_client.add_subscriber_channel(json_obj['data']['channel'], self.conn)
        except (KeyError, TypeError):
            pass

    def remove(self):
        for channel in self.conn.subscribe_list:
            self.conn.pika_client.remove_subscriber_channel(channel, self.conn)
        self.conn.subscribe_list = None

    def is_access(self, token):

        pass

