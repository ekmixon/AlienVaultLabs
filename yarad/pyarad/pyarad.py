
# pyarad - py lib to use yarad daemon
# AlienVault Labs - https://github.com/jaimeblasco/AlienvaultLabs
#
# Licensed under GNU/GPLv3
# aortega@alienvault.com

import socket
import ast
import uuid
import os
import zlib

class pyarad:
	def __init__(self):
		pass

	# Connections handlers
	def init_network_socket(self, host, port=3369):
		self.net_socket = True
		self.initialized = True
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((host, port))
	def init_unix_socket(self, socket_file="/tmp/yarad.ctl"):
		self.net_socket = False
		self.initialized = True
		self.conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.conn.connect(socket_file)
	def close(self):
		if self.initialized != True:
			return None
		self.conn.send("!close")
		self.conn.close()
		self.initialized = False

	# Functions to dump files
	def zdump_file(self, filename):
		with open(filename, "rb") as f:
			data = f.read()
		return zlib.compress(data, 9)
	def zdump_stream(self, filebuffer):
		return zlib.compress(filebuffer, 9)

	# Scanning functions
	def scan_file(self, filename):
		if self.initialized != True:
			return None
		if os.path.exists(filename):
			if self.net_socket == True:
				self.conn.send(self.zdump_file(filename))
			else:
				self.conn.send(os.path.abspath(filename))
			return ast.literal_eval(self.conn.recv(1024))
		else:
			return []
	def scan_stream(self, filebuffer):
		if self.initialized != True:
			return None
		if self.net_socket == True:
			self.conn.send(self.zdump_stream(filebuffer))
		else:
			filename = f"/tmp/.{str(uuid.uuid4())}"
			with open(filename, "wb") as f:
				f.write(filebuffer)
			self.conn.send(filename)
		result = ast.literal_eval(self.conn.recv(1024))
		if self.net_socket == False:
			os.unlink(filename)
		return result

