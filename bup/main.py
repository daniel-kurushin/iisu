import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep

from kup import KUP

class PowerRequestHandler(BaseHTTPRequestHandler):
	try:
		from bup import BUP
		bup = BUP()
		
		assert bup.state['kup']['present'] == True
		kup = KUP(bup)
	except Exception as e:
		raise e

	def get_state(self):
		x = self.kup.measure()
		x.update(self.kup.get_state())
		return x

	def do48v_on(self):
		return self.kup.do48v_on()

	def do48v_off(self):
		return self.kup.do48v_off()

	
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
		elif self.path.startswith('/state') or self.path.startswith('/measure'):
			self.to_json(self.get_state())
		elif self.path.startswith('/48v/on'):
			self.to_json(self.do48v_on())
		elif self.path.startswith('/48v/off'):
			self.to_json(self.do48v_off())
		elif self.path == "/exit":
			self.load_str('')
			global need_to_exit
			need_to_exit = True
			self.server.server_close()
			exit(0)
		else:
			self.load_file('index.html')

if __name__ == "__main__":
	server = HTTPServer(('0.0.0.0', 8001), PowerRequestHandler)
	try:
		server.serve_forever()
	except:
		need_to_exit = True
