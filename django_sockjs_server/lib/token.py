from hashlib import md5
from django_sockjs_server.lib.config import SockJSServerSettings

class Token(object):
    def __init__(self):
        self.config = SockJSServerSettings()

    def get_secret_data(self, data):
        token = self.config.secret_key + data
        return "%s" % md5(token).hexdigest()

    def get_data(self, token, data):
        if token == self.get_secret_data(data):
            return data
        raise KeyError
