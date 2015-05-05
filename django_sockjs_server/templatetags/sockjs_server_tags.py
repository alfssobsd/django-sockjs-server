from random import choice
from django import template
from django_sockjs_server.lib.config import SockJSServerSettings
from django_sockjs_server.lib.token import Token

register = template.Library()

@register.simple_tag(name='sockjs_auth_token')
def sockjs_auth_token(room_name, unq_id=None):
    token = Token()
    if unq_id:
        return token.get_secret_data(room_name+str(unq_id))
    return token.get_secret_data(room_name)


@register.simple_tag(name='sockjs_server_url')
def sockjs_server_url():
    config = SockJSServerSettings()
    return choice(config.sockjs_url)
