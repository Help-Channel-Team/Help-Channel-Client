import websocket 

proxy_host = ""
proxy_port = ""
proxy_auth = {"username":"Usuario","password":"password"}

ws = websocket.WebSocket()

if not proxy_host:
	ws.connect("wss://helpchannel.cygitsolutions.com/wsServer")
else:
        ws.connect("wss://helpchannel.cygitsolutions.com/wsServer",http_proxy_host=proxy_host,http_proxy_port=proxy_port,http_proxy_auth=proxy_auth)
send_string = "ID:PRUEBADEPROXY"
print "Enviando: ",send_string
ws.send(send_string)
result = ws.recv()
print "Recibiendo: ",result
ws.close()
