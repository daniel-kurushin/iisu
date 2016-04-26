import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler, urllib
from threading import Thread
from time import sleep
from datetime import datetime

from biu.biu import BIU
from biu.kru import KRU
from biu.khc import KHC
from bup.bup import BUP
from bup.kup import KUP
from cv.cv import CV 
from bins.bins import BINS
from base64 import encodebytes

class IISURequestHandler(BaseHTTPRequestHandler):
	err404 = dict(
		error = 'wrong path',
		code = 404,
	)
	exclude_ports = []
	biu = BIU(exclude_ports) ; exclude_ports += [biu.port]
	bup = BUP(exclude_ports) ; exclude_ports += [bup.port]
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

	bins = BINS(exclude_ports)
	try:
		assert bins.state['0x70']['present'] == True
		assert bins.state['0x33']['present'] == True
	except Exception as e:	
		print(type(e), e, file=sys.stderr)
		bins.stop()
		exit(1)

	def get_state(self):
		_ = {}
		for x in [self.kru, self.khc, self.kup, self.cv, self.bins]:
			_.update({x.NAME:x.get_state()})
		return _
	
	def get_distances(self):
		return self.khc.get_distances()

	def get_encoders(self):
		return None

	def do_steer(self, data):
		print(data, file = sys.stderr)
		x = int(data['req_str_pos'][0])
		y = self.kru.get_pos()['pos']
		if abs(x-y) > 1: return self.kru.steer(pos = x)
		else: return self.kru.steer(pos = y)

	def do_flick(self, data):
		print(data, file = sys.stderr)
		side = int(data['side'][0])
		mode = int(data['mode'][0])
		return self.kru.flick(side, mode)

	def do_gooo(self, data):
		print(data, file = sys.stderr)
		req_acc_pos = int(data['req_acc_pos'][0])
		if req_acc_pos != 0: self.do_power_48v('on')
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

	def do_kru_restart(self):
		return self.kru.restart()

	def do_stop_engine(self):
		x = self.khc.stop_engine()
		self.khc.brakes(rgt = 0,lgt = 0,frw = 1)
		self.do_power_48v('off')
		return x

	def get_power(self, ):
		return self.kup.get_state()

	def do_power_48v(self, pon = 'on'):
		if pon == 'off':
			return self.kup.do48v_off()
		else:
			return self.kup.do48v_on()

	def set_acc_steer(self, data):
		print(data, file = sys.stderr)
		_ = {}
		_.update(self.do_steer(data))
		_.update(self.do_gooo(data))
		return _
		y = self.get_steerpos()

	def do_scan(self):
		return self.cv.do_scan(-1,1)
	
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
		self.wfile.write(str.encode(json.dumps(data, indent = 4)))

	def to_jpeg(self,data):
		self.send_response(200)
		self.send_header('Content-type', 'image/jpeg')
		self.end_headers()
		self.wfile.write(data)

	def process_move_urls(self, data):
		if self.path.startswith('/move/set_acc_steer'):
			self.to_json(self.set_acc_steer(data))
		elif self.path.startswith('/move/set_acc_course'):
			pass
		else:
			self.to_json(self.err404) 

	def process_flick_urls(self, data = None):
		if self.path.startswith('/flick/stop'):
			_ = self.do_stop_flick()
		elif self.path.startswith('/flick/left'):
			self.do_stop_flick()
			_ = self.do_flick(dict(side = [0], mode = [0]))
		elif self.path.startswith('/flick/right'):
			self.do_stop_flick()
			_ = self.do_flick(dict(side = [1], mode = [0]))
		elif self.path.startswith('/flick/both'):
			self.do_stop_flick()
			_ = self.do_flick(dict(side = [2], mode = [0]))
		elif self.path.startswith('/flick/state'):
			_ = self.kru.get_state()
		else:
			_ = self.err404

		try:
			res = dict(
				flickersMode = _['flickerState'] != 0,
			)
			if _['flickersMode'] == 0:
				res.update({'flickersSide': 'left'})
			elif _['flickersMode'] == 1:
				res.update({'flickersSide': 'right'})
			elif _['flickersMode'] == 2:
				res.update({'flickersSide': 'both'})
		except KeyError:
			res = {'ok':False}
			
		self.to_json(res)

	def process_steer_urls(self, data = None):
		if self.path.startswith('/steer/set_pos'):
			self.to_json(self.do_steer(data))
		elif self.path.startswith('/steer/get_pos'):
			self.to_json(self.kru.get_pos())
		elif self.path.startswith('/steer/restart'):
			self.to_json(self.do_kru_restart())
		else:
			self.to_json(self.err404) 

	def process_engine_urls(self, data = None):
		if self.path.startswith('/engine/stop'):
			self.to_json(self.do_stop_engine())
		elif self.path.startswith('/engine/gooo'):
			self.to_json(self.do_gooo(data))
		elif self.path.startswith('/engine/reverse'):
			self.to_json(self.do_reverse(data))
		elif self.path.startswith('/engine/brakes'):
			self.to_json(self.do_brakes(data))
		elif self.path.startswith('/engine/get_pos'):
			_ = self.khc.get_state()
			if _['is_reverse']: k = -1 
			else: k = 1
			self.to_json(dict(ok=_['ok'],currentAccelPos=k*_['currentAccelPos']))
		else:
			self.to_json(self.err404)

	def process_state_urls(self, data = None):
		if self.path == '/state':
			self.to_json(self.get_state())
		elif self.path.startswith('/state/encoders'):
			self.to_json(self.get_encoders())
		elif self.path.startswith('/state/distances'):
			self.to_json(self.get_distances())
		else:
			self.to_json(self.err404)

	def process_power_urls(self, data = None):
		if self.path.startswith('/power/measure'):
			self.to_json(self.get_power())
		elif self.path.startswith('/power/48v/off'):
			self.to_json(self.do_power_48v('off'))
		elif self.path.startswith('/power/48v/on'):
			self.to_json(self.do_power_48v('on'))
		else:
			self.to_json(self.err404)

	def process_bins_urls(self, data = None):
		if self.path.startswith('/orientation/get'):
			self.to_json(self.bins.get_state())

	def process_view_urls(self, data = None):
		if self.path.startswith('/view/left'):
			_ = self.cv.get_left()
			if _['ok']: self.to_jpeg(_['img'])
		elif self.path.startswith('/view/right'):
			_ = self.cv.get_right()
			if _['ok']: self.to_jpeg(_['img'])
		elif self.path.startswith('/view/360'):
			_ = self.cv.get_wide()
			if _['ok']: self.to_jpeg(_['img'])
		elif self.path.startswith('/view/picture'):
			_ = self.cv.picture()
			if _['ok']: self.to_jpeg(_['img'])
		elif self.path.startswith('/view/set_current_cam'):
			self.to_json(self.cv.set_current_cam(self.path.split('/')[-1]))
		elif self.path.startswith('/view/rotate'):
			A,B=[int(a.strip(')')) for a in self.path.split('(')[1:]]
			_ = self.cv.do_rotate(A,B)
			self.to_json(_)
		else:
			self.to_json(self.err404)

	def do_POST(self):
		print(self.path, file = sys.stderr)
		data = urllib.parse.parse_qs(
			self.rfile.read(
				int(self.headers.get('content-length'))
			).decode('utf-8')
		)
		if self.path.startswith('/steer'):
			self.process_steer_urls(data)
		elif self.path.startswith('/engine'):
			self.process_engine_urls(data)
		elif self.path.startswith('/power'):
			self.process_power_urls(data)
		elif self.path.startswith('/move'):
			self.process_move_urls(data)
		else:
			self.to_json(self.err404)

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
		elif self.path.startswith('/ping'):
			self.to_json({'time':str(datetime.now())})
		elif self.path.startswith('/steer'):
			self.process_steer_urls()
		elif self.path.startswith('/engine'):
			self.process_engine_urls()
		elif self.path.startswith('/state'):
			self.process_state_urls()
		elif self.path.startswith('/power'):
			self.process_power_urls()
		elif self.path.startswith('/move'):
			self.process_move_urls()
		elif self.path.startswith('/flick'):
			self.process_flick_urls()
		elif self.path.startswith('/orientation'):
			self.process_bins_urls()
		elif self.path.startswith('/view'):
			self.process_view_urls()
		elif self.path.startswith('/scan'):
			self.to_json(self.do_scan())
		elif self.path == "/exit":
			self.load_str('')
			global need_to_exit
			need_to_exit = True
			self.server.server_close()
			exit(0)
		else:
			self.load_file('index.html')


if __name__ == "__main__":
	server = HTTPServer(('0.0.0.0', 8000), IISURequestHandler)
	try:
		server.serve_forever()
	except:
		need_to_exit = True
