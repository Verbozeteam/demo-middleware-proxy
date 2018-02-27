#!.env/bin/python

import logging
from websocket_server import WebsocketServer
from threading import Lock

ALL_CLIENTS = {}
GLOBAL_LOCK = Lock()

def new_client(client, server):
	global ALL_CLIENTS, GLOBAL_LOCK
	GLOBAL_LOCK.acquire()
	try:
		ALL_CLIENTS[client["id"]] = client
	except Exception as e:
		print (e)
	finally:
		GLOBAL_LOCK.release()

def client_left(client, server):
	global ALL_CLIENTS, GLOBAL_LOCK
	GLOBAL_LOCK.acquire()
	try:
		del ALL_CLIENTS[client["id"]]
	except Exception as e:
		print (e)
	finally:
		GLOBAL_LOCK.release()

def on_message(client, server, message):
	global ALL_CLIENTS, GLOBAL_LOCK
	GLOBAL_LOCK.acquire()
	try:
		for clid in list(ALL_CLIENTS.keys()):
			if clid != client["id"]:
				server.send_message(ALL_CLIENTS[clid], message)
	except Exception as e:
		print (e)
	finally:
		GLOBAL_LOCK.release()


server = WebsocketServer(7986, host='0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(on_message)
server.run_forever()
