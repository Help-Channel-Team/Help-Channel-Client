#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, LogTrapTestCase
from wstunnel.filters import DumpFilter, FilterException
from wstunnel.test import EchoServer, EchoClient, RaiseFromWSFilter, RaiseToWSFilter, setup_logging, clean_logging, \
    fixture, DELETE_TMPFILE
from wstunnel.client import WSTunnelClient, WebSocketProxy
from wstunnel.server import WSTunnelServer
from wstunnel.toolbox import hex_dump, random_free_port

if len(sys.argv) == 3:
	port = sys.argv[1] 
	WSEndPoint = sys.argv[2] 
else:
	print "Usage python wstunnel.py PORT WSENDPOINT"
	sys.exit(0)
#port = 6000
#WSEndPoint = "wss://helpchannel.cygitsolutions.com/wsServer"

print "Initializing Tunnel from local TCP port " + port + " to Websocket " + WSEndPoint

clt_tun = WSTunnelClient(proxies={port: WSEndPoint},family=socket.AF_INET)
clt_tun.install_filter(DumpFilter(handler={"filename": "/tmp/clt_log"}))
clt_tun.start()
IOLoop.instance().start()
