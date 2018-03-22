#!/usr/bin/env python

import pycos, socket, sys, time
import websocket
import ConfigParser
import gettext
import platform
import os
import os.path
import urllib

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


def ws_send(conn,ws, task=None):
    task.set_daemon()

    thread_pool = pycos.AsyncThreadPool(1)	

    while True:
        try:
	    #print("Esperando datos en websocket")
            line = yield thread_pool.async_task(ws.recv)
        except:
            break
        if not line:
	    #print("No se han recibido datos en el websocket")	
            break
	#print('Recibido %s desde el websocket' % line)	
	yield conn.send(line)        

def client_send(conn,ws, task=None):
    task.set_daemon()

    while True:
        try:
            #print("Esperando datos en el socket")
            line = yield conn.recv(1024)	
        except:
            break
        if not line:
            break
	#print('Recibido %s en el socket' % line)
	ws.send_binary(line)        

def hcwst(host, port,repeater_ws,proxy_host,proxy_port,proxy_username,proxy_password,task=None):

    task.set_daemon()
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)	
    sock = pycos.AsyncSocket(sock)
    sock.bind((host, int(port)))
    sock.listen(1)
    print('server at %s' % str(sock.getsockname()))

    ws = websocket.WebSocket()

    if not proxy_host:
	ws.connect(repeater_ws, subprotocols=["binary"],sockopt=(socket.IPPROTO_TCP, socket.TCP_NODELAY))
    else:
        ws.connect(repeater_ws,http_proxy_host=proxy_host,http_proxy_port=proxy_port,http_proxy_auth=proxy_auth, subprotocols=["binary"],sockopt=(socket.IPPROTO_TCP, socket.TCP_NODELAY))	
  
    print('Websocket connected to wss://helpchannel.cygitsolutions.com/wsServer')

    conn, addr = yield sock.accept()
    pycos.Task(client_send, conn,ws)
    pycos.Task(ws_send, conn,ws)


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser.ConfigParser()
    config.read(BASE_DIR + "/config.ini")

    proxy_host = config_section_map("ServerConfig")['proxy_host']
    proxy_port = config_section_map("ServerConfig")['proxy_port']
    proxy_username = config_section_map("ServerConfig")['proxy_username']
    proxy_password = config_section_map("ServerConfig")['proxy_password']

    repeater_ws = config_section_map("TunnelConfig")['tunnel_url']
    local_tunnel_port = config_section_map("TunnelConfig")['local_port']

    proxy_auth=(proxy_username,proxy_password)

    host, port = '127.0.0.1', int(local_tunnel_port)
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    pycos.Task(hcwst, host, local_tunnel_port,repeater_ws,proxy_host,proxy_port,proxy_username,proxy_password)
    if sys.version_info.major > 2:
        read_input = input
    else:
        read_input = raw_input
    while True:
        try:
            cmd = read_input('Pulsa "quit" o "exit" para salir: ').strip().lower()
            if cmd.strip().lower() in ('quit', 'exit'):
                break   
        except:
            break
