#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import ConfigParser
import gettext
import platform
import os
import os.path
import urllib

def config_section_map(section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
config = ConfigParser.ConfigParser()
config.read(BASE_DIR + "/config.ini")

proxy_host = config_section_map("ServerConfig")['proxy_host']
proxy_port = config_section_map("ServerConfig")['proxy_port']
proxy_username = config_section_map("ServerConfig")['proxy_username']
proxy_password = config_section_map("ServerConfig")['proxy_password']

proxy_connection_string = 'http://' + proxy_username + ":" + proxy_password + "@" + proxy_host + ":" + proxy_port

os.environ['http_proxy'] = '127.0.0.1'
os.environ['https_proxy'] = '127.0.0.1'	

if proxy_host:
	print "Proxy mode"
	proxy = urllib2.ProxyHandler()
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
	urllib2.install_opener(opener)
  
urllib2.urlopen("https://google.es")

print "Test completed"
