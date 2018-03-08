#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import ConfigParser
import gettext
import platform
import os
import os.path
import urllib

from tornado.ioloop import IOLoop
from tornado.testing import AsyncTestCase, LogTrapTestCase
from wstunnel.filters import DumpFilter, FilterException
from wstunnel.test import EchoServer, EchoClient, RaiseFromWSFilter, RaiseToWSFilter, setup_logging, clean_logging, \
    fixture, DELETE_TMPFILE
from wstunnel.client import WSTunnelClient, WebSocketProxy
from wstunnel.server import WSTunnelServer
from wstunnel.toolbox import hex_dump, random_free_port

# Function to get dictionary with the values of one section of the configuration file
def config_section_map(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1

port = "6000"
WSEndPoint = "wss://helpchannel.cygitsolutions.com:443/wsServer"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
config = ConfigParser.ConfigParser()
config.read(BASE_DIR + "/config.ini")

proxy_host = config_section_map("ServerConfig")['proxy_host']
proxy_port = config_section_map("ServerConfig")['proxy_port']
proxy_username = config_section_map("ServerConfig")['proxy_username']
proxy_password = config_section_map("ServerConfig")['proxy_password']
proxy_auth_mode = config_section_map("ServerConfig")['proxy_auth_mode']


print "Initializing Tunnel from local TCP port " + port + " to Websocket " + WSEndPoint

clt_tun = WSTunnelClient(proxies={port: WSEndPoint},family=socket.AF_INET)
clt_tun.install_filter(DumpFilter(handler={"filename": "/tmp/clt_log"}))
clt_tun.start()
IOLoop.instance().start()
