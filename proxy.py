#!.env/bin/python

import logging
import json
from websocket_server import WebsocketServer
from threading import Lock
import sys, os
from functools import reduce
import netifaces

import time, random, signal

ALL_CLIENTS = {}
GLOBAL_LOCK = Lock()
MIDDLEWARE_ROOM_ID = json.load('../middleware/blueprint.json')["id"]

LOCAL_IPS = ['localhost', '0.0.0.0']
ifaces = []
for i in netifaces.interfaces():
	try:
		ip = netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']
		LOCAL_IPS.append(ip)
	except: pass

def new_client(client, server):
	global ALL_CLIENTS, GLOBAL_LOCK
	GLOBAL_LOCK.acquire()
	try:
		ALL_CLIENTS[client["id"]] = client
		print ("PROXY: Client connected: {} {}".format(client["id"], client["address"]))
	except Exception as e:
		print (e)
	finally:
		GLOBAL_LOCK.release()

def client_left(client, server):
	global ALL_CLIENTS, GLOBAL_LOCK
	GLOBAL_LOCK.acquire()
	try:
		del ALL_CLIENTS[client["id"]]
		print ("PROXY: Client disconnected: {}".format(client["id"]))
	except Exception as e:
		print (e)
	finally:
		GLOBAL_LOCK.release()

def on_message(client, server, message):
	global ALL_CLIENTS, GLOBAL_LOCK, MIDDLEWARE_ROOM_ID, LOCAL_IPS
	GLOBAL_LOCK.acquire()
	try:
		if reduce(lambda a,b: a and b, map(lambda ip: ip not in client["address"][0], LOCAL_IPS)): # if the client address is not local (that is, not the aggregator running on this same pi)
			# add a target room id to it as if it came from www.verboze.com going to the aggregator
			message = json.loads(message)
			message["__room_id"] = MIDDLEWARE_ROOM_ID
			message = json.dumps(message)
		# forward the message to all others
		for clid in list(ALL_CLIENTS.keys()):
			if clid != client["id"]:
				server.send_message(ALL_CLIENTS[clid], message)
				print ("PROXY: [{} => {}]".format(client["id"], clid))
	except Exception as e:
		print ("ERROR IN FORWARDING ", e)
	finally:
		GLOBAL_LOCK.release()


server = WebsocketServer(7986, host='0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(on_message)
server.run_forever()
