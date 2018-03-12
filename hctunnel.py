#!/usr/bin/env python

import pycos, socket, sys, time
import websocket

def ws_send(conn,ws, task=None):
    task.set_daemon()

    thread_pool = pycos.AsyncThreadPool(1)	

    while True:
        try:
	    print("Esperando datos en websocket")
            line = yield thread_pool.async_task(ws.recv)
        except:
            break
        if not line:
	    print("No se han recibido datos en el websocket")	
            break
	print('Recibido %s desde el websocket' % line)	
	yield conn.send(line)        

def client_send(conn,ws, task=None):
    task.set_daemon()

    while True:
        try:
            print("Esperando datos en el socket")
            line = yield conn.recv(1024)	
        except:
            break
        if not line:
            break
	print('Recibido %s en el socket' % line)
	ws.send(line)        

def hcwst(host, port, task=None):
    task.set_daemon()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)	
    sock = pycos.AsyncSocket(sock)
    sock.bind((host, port))
    sock.listen(1)
    print('server at %s' % str(sock.getsockname()))

    ws = websocket.WebSocket()
    ws.connect('wss://helpchannel.cygitsolutions.com/wsServer',subprotocols=["binary"])
    print('Websocket connected to wss://helpchannel.cygitsolutions.com/wsServer')

    conn, addr = yield sock.accept()
    pycos.Task(client_send, conn,ws)
    pycos.Task(ws_send, conn,ws)


if __name__ == '__main__':

    host, port = '', 6000
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    pycos.Task(hcwst, host, port)
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
