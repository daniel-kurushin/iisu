import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep

from biu.biu import BIU
from biu.kru import KRU
from biu.khc import KHC
from bup.bup import BUP
from bup.kup import KUP
from cv.cv import CV 
from bins.bins import BINS

class BIURequestHandler(BaseHTTPRequestHandler):
	biu = BIU()
	bup = BUP()

	try:
		assert biu.state['kru']['present'] == True
	except Exception as e:
		print(type(e), e, file=sys.stderr)
		exit(1)
	finally:
		kru = KRU(biu)
	
	try:
		assert biu.state['khc']['present'] == True
	except Exception as e:
		print(type(e), e, file=sys.stderr)
		exit(1)
	finally:
		khc = KHC(biu)
	
	try:
		assert bup.state['kup']['present'] == True
	except Exception as e:
		print(type(e), e, file=sys.stderr)
		exit(1)
	finally:
		kup = KUP(bup)

	cv = CV(url='http://192.168.0.198:8000')
	try:
		assert cv.state['state'] == 'NORMAL_OP'
	except Exception as e:
		print(type(e), e, file=sys.stderr)
		exit(1)

	bins = BINS()
	try:
		assert bins.state['0x70']['present'] == True
		assert bins.state['0x33']['present'] == True
	except Exception as e:	
		print(type(e), e, file=sys.stderr)
		bins.stop()
		exit(1)


	def to_port(self, data):
		return None

	def from_port(self):
		return None

	def get_state(self):
		_ = {}
		for x in [self.kru, self.khc, self.kup, self.cv]:
			_.update({x.name:x.get_state()})
		return _
	
	def get_distances(self):
		return self.khc.get_distances()

	def get_encoders(self):
		return None

	def get_steerpos(self):
		return self.kru.get_pos()

	def do_steer(self, data):
		print(data, file = sys.stderr)
		x = int(data['pos'][0])
		return self.kru.steer(pos = x)

	def do_flick(self, data):
		print(data, file = sys.stderr)
		side = int(data['side'][0])
		mode = int(data['mode'][0])
		return self.kru.flick(side, mode)

	def do_gooo(self, data):
		print(data, file = sys.stderr)
		req_acc_pos = int(data['req_acc_pos'][0])
		rgt_brk = int(data['rgt_brk'][0])
		lgt_brk = int(data['lgt_brk'][0])
		return self.khc.gooo(req_acc_pos, rgt_brk, lgt_brk)

	def do_brakes(self, data):
		print(data, file = sys.stderr)
		rgt = int(data['rgt'][0])
		lgt = int(data['lgt'][0])
		frw = int(data['frw'][0])
		return self.khc.brakes(rgt,lgt,frw)

	def do_reverse(self, data):
		print(data, file = sys.stderr)
		v = int(data['v'][0])
		return self.khc.reverse(v)

	def do_stop_flick(self):
		return self.kru.stop_flick()

	def do_restart(self):
		return self.kru.restart()

	def do_stop_engine(self):
		return self.khc.stop_engine()

	
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

	def do_POST(self):
		print(self.path, file = sys.stderr)
		data = urllib.parse.parse_qs(
			self.rfile.read(
				int(self.headers.get('content-length'))
			).decode('utf-8')
		)
		if self.path.startswith('/steer'):
			self.to_json(self.do_steer(data))
		elif self.path.startswith('/flick'):
			self.to_json(self.do_flick(data))
		elif self.path.startswith('/gooo'):
			self.to_json(self.do_gooo(data))
		elif self.path.startswith('/reverse'):
			self.to_json(self.do_reverse(data))
		elif self.path.startswith('/brakes'):
			self.to_json(self.do_brakes(data))
		else:
			self.load_str('wrong path')

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
		elif self.path.startswith('/encoders'):
			self.to_json(self.get_encoders())
		elif self.path.startswith('/distances'):
			self.to_json(self.get_distances())
		elif self.path.startswith('/steerpos'):
			self.to_json(self.get_steerpos())
		elif self.path.startswith('/stop_flick'):
			self.to_json(self.do_stop_flick())
		elif self.path.startswith('/kru_restart'):
			self.to_json(self.do_restart())
		elif self.path.startswith('/stop_engine'):
			self.to_json(self.do_stop_engine())
		elif self.path == "/exit":
			self.load_str('')
			global need_to_exit
			need_to_exit = True
			self.server.server_close()
			exit(0)
		else:
			self.load_file('index.html')


if __name__ == "__main__":
	server = HTTPServer(('0.0.0.0', 8000), BIURequestHandler)
	try:
		server.serve_forever()
	except:
		need_to_exit = True
