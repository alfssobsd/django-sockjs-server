# Django SockJS-server 

Simple sockjs server for django.

## Requirements:

* sockjs-tornado >= 1.0.0
* pika >= 0.9.12
* django >= 1.4

## Installation:
```
pip install django-sockjs-server
```

Add django-sockjs-server to your INSTALLED_APPS in settings.py

```
  INSTALLED_APPS = (
       ...
       'django_sockjs_server',
       ...
  )
  ```

Define ```DJANGO_SOCKJS_SERVER``` in ```settings.py```.

```
  DJANGO_SOCKJS_SERVER = {
      'rabbitmq_server_host': 'localhost',
      'rabbitmq_user': 'guest',
      'rabbitmq_password': 'guest',
      'rabbitmq_server_port': 5672,
      'rabbitmq_server_vhost': '/',
      'rabbitmq_exhange_name': 'sockjs',
      'rabbitmq_exchange_type': 'fanout',
      'listen_addr': '0.0.0.0',
      'listen_port': 8083,
      'listen_location': '/ws'
      'secret_key': 'xe4pa7gysp4phe2rhyd',
      'sockjs_url': 'http://localhost:8083/ws'
  }
```
* rabbitmq_server_host - rabbitmq server
* rabbitmq_user - rabbitmq user
* rabbitmq_password - rabbitmq password
* rabbitmq_server_port - rabbitmq port
* rabbitmq_server_vhost - rabbitmq vhost
* rabbitmq_exhange_name - exchange name
* rabbitmq_exchange_type - type exchange
* listen_addr - listen sockjs server address
* listen_port - listen sockjs server port
* listen_location - listen sockjs server location
* secret_key - salt for subscribe
* sockjs_url - path for client sockjs

