#!/usr/bin/env python

# client and server tasks communicating with message passing
# (asynchronous concurrent programming);
# see https://pycos.sourceforge.io/pycos.html for details.

import sys, random
import pycos

def server_proc(task=None):
    task.set_daemon()
    while True:
        msg = yield task.receive()
        print('Received %s' % (msg))

msg_id = 0

def client_proc(server, n, task=None):
    global msg_id
    for i in range(3):
        yield task.suspend(random.uniform(0.5, 3))
        msg_id += 1
        server.send('%d: %d / %d' % (msg_id, n, i))

# create server
server = pycos.Task(server_proc)
# create 10 clients
for i in range(10):
    pycos.Task(client_proc, server, i)
