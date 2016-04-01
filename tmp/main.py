# -*- coding: utf-8 -*-
import json
import subprocess
import sys

from threading import Thread
from urllib.request import urlopen
from http.server import HTTPServer, BaseHTTPRequestHandler, urllib

from bins import BINS
from power import Power
from steer import Steer
from march import March
from brake import Brake
from rfind import Rfind
from flick import Flick
from speed import Speed

from cv import CV

class IISURequestHandler(BaseHTTPRequestHandler):
	bins = BINS()
	cv = CV()

	def load_file(self, name, context=None, content_type='text/html'):
		self.send_response(200)
		self.send_header('Content-type', content_type)
		self.end_headers()
		data = ''
		with open(name, 'rb') as _file:
			data = _file.read()
		if context:
			for key in context:
				data = data.replace(
					bytes(key, 'utf-8'),
					bytes(context[key], 'utf-8')
				)
		self.wfile.write(data)

	def load_str(self, data):
		self.send_response(200)
		self.end_headers()
		self.wfile.write(bytes(data, 'utf-8'))

	def to_json(self, data):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(str.encode(json.dumps(data)))

	def do_GET(self):
		print(self.path, file = sys.stderr)
		if self.path.endswith('png'):
			self.load_file(self.path.lstrip('/'), content_type='image/png')
		elif self.path.endswith('jpg'):
			self.load_file(self.path.lstrip('/'), content_type='image/jpeg')
		elif self.path.startswith('/static'):
			content_type = 'text/html'
			if self.path.endswith('jpg'):
				content_type = 'image/jpeg'
			elif self.path.endswith('css'):
				content_type = 'text/css'
			self.load_file(self.path.lstrip('/'), content_type=content_type)
		elif self.path.startswith('/state'):
			self.to_json(self.get_state())
		elif self.path == "/exit":
			self.load_str('')
			global need_to_exit
			need_to_exit = True
			self.server.server_close()
			exit(0)
		else:
			self.load_file('index.html')

	def do_POST(self):
		print(self.path, file = sys.stderr)
		data = urllib.parse.parse_qs(
			self.rfile.read(
				int(self.headers.get('content-length'))
			).decode('utf-8')
		)
		if self.path.startswith('/recognize'):
			self.to_json(self.do_recognize(data))
		elif self.path.startswith('/cloud'):
			self.to_json(self.do_cloud(data))
		else:
			self.load_str('wrong path')

	def log_message(self, format, *args):
		return


if __name__ == "__main__":
	server = HTTPServer(('0.0.0.0', 8000), IISURequestHandler)
	try:
		server.serve_forever()
	except:
		need_to_exit = True

