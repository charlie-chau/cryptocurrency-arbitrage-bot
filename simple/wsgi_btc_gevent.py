#!/usr/bin/env python

from gevent.wsgi import WSGIServer
from iotbtc_endpoint import app

http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()
