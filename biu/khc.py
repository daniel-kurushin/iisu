import sys
from struct import pack, unpack
from time import sleep

class KHC(object):
	NAME = 'KHC'

	cmd_inc_engine    = b'\xae\xae\x01\x00\x01\x08\x00' # увеличить обороты и подтвердить результат
	cmd_dec_engine    = b'\xae\xae\x01\x00\x02\x08\x00' # уменьшить обороты и подтвердить результат
	cmd_stop_engine   = b'\xae\xae\x01\x00\x07\x07\x00' # остановка
	cmd_get_distances = b'\xae\xae\x01\x00\x08\x07\x00' # вернуть расстояния от дальномеров
	cmd_get_encoders  = b'\xae\xae\x01\x00\x09\x07\x00' # энкодеры колес
	cmd_reverse       = b'\xae\xae\x01\x00\x0a\x08\x00' # вкл-выкл реверса
	cmd_brakes        = b'\xae\xae\x01\x00\x11\x0a\x00' # тормоза
														# | | +--- правый 0 - выкл, 1 - вкл
														# | +----- левый
														# +------- передний
	cmd_get_state     = b'\xae\xae\x01\x00\xff\x07\x00' # вернуть состояние КХЧ
														# currentAccelPos - обороты
														# is_frw_brake ff - вкл передний тормоз 00 - выкл
														# is_lgt_brake ff - вкл левый тормоз    00 - выкл
														# is_rgt_brake ff - вкл правый тормоз   00 - выкл
														# is_reverse   ff - вкл реверс          00 - выкл
														# enc_sec - срабатываний энкодера в сек
														# enc_min - срабатываний энкодера в мин

	currentAccelPos = 0											

	def parse_distances(self, x):
		return dict(
			ok = True,
			rear  = int(unpack('<B', x[3:4])[0]) * 128.0 / 58.0 / 100.0,
			left  = int(unpack('<B', x[4:5])[0]) * 128.0 / 58.0 / 100.0,
			front = int(unpack('<B', x[5:6])[0]) * 128.0 / 58.0 / 100.0,
			right = int(unpack('<B', x[6:7])[0]) * 128.0 / 58.0 / 100.0,
		)	
	
	def parse_engine(self, x):
		return dict(
			ok = True,
			currentAccelPos = int(unpack('<b', x[3:4])[0]),
		)

	def parse_reverse(self, x):
		return dict(
			ok = True,
			is_reverse = bool(unpack('<b', x[3:4])[0]),
		)

	def parse_brakes(self, x):
		return dict(
			ok = True,
			is_frw_brake    = bool(unpack('<b', x[3:4])[0]),
			is_lgt_brake    = bool(unpack('<b', x[4:5])[0]),
			is_rgt_brake    = bool(unpack('<b', x[5:6])[0]),
		)

	def parse_encoders(self, x):
		return dict(a=0)

	def parse_state(self, x):
		return dict(
			ok = True,
			currentAccelPos = int(unpack('<b', x[3: 4])[0]),
			is_frw_brake    = bool(unpack('<b', x[4: 5])[0]),
			is_lgt_brake    = bool(unpack('<b', x[5: 6])[0]),
			is_rgt_brake    = bool(unpack('<b', x[6: 7])[0]),
			is_reverse      = bool(unpack('<b', x[7: 8])[0]),
			enc_sec         = int(unpack('<b', x[8: 9])[0]),
			enc_min         = int(unpack('<b', x[9:10])[0]),
		)

	def inc_engine(self):
		cmd = self.cmd_inc_engine
		v = pack('>b', 1)
		print('>>>', cmd, v, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(v)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		self.currentAccelPos += 1
		return self.parse_engine(ret)

	def dec_engine(self):
		cmd = self.cmd_dec_engine
		v = pack('>b', 1)
		print('>>>', cmd, v, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(v)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		self.currentAccelPos -= 1
		return self.parse_engine(ret)

	def gooo(self, req_acc_pos = 31, rgt_brk = 0, lgt_brk = 0):
		backward_needed = req_acc_pos < 0
		acc_pos = abs(req_acc_pos)
		stop_needed    = acc_pos == 0
		self.state = self.get_state()
		self.brakes(rgt = rgt_brk, lgt = lgt_brk, frw = 0)
		if self.state['is_reverse'] != backward_needed and backward_needed: 
			print(backward_needed, self.state['is_reverse'])
			self.reverse(1)
		if self.state['is_reverse'] != backward_needed and not backward_needed: self.reverse(0)
		self.state = self.get_state()
		D = int(acc_pos - self.state['currentAccelPos'])
		if D > 0: f = self.inc_engine
		else: f = self.dec_engine
		for i in range(abs(D)): f()
		_ = self.get_state()
		pos = _['currentAccelPos']
		if _['is_reverse']: pos = -1 * pos
		return dict(
			ok = pos == req_acc_pos,
			requiredAccelPos = req_acc_pos,
			currentAccelPos = pos,
		)

	def stop_engine(self):
		cmd = self.cmd_stop_engine
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		self.currentAccelPos = 0
		return self.parse_engine(ret)

	def reverse(self, v = 1):
		cmd = self.cmd_reverse
		v = pack('>b', v)
		print('>>>', cmd, v, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(v)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		return self.parse_reverse(ret)

	def brakes(self, rgt = 0, lgt = 0, frw = 1):
		cmd = self.cmd_brakes
		rgt = pack('>b', rgt)
		lgt = pack('>b', lgt)
		frw = pack('>b', frw)
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(frw)
		self.port.write(rgt)
		self.port.write(lgt)
		ret = self.port.read(6)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 6
		return self.parse_brakes(ret)

	def get_encoders(self):
		cmd = self.cmd_get_distances
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(7)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 7
		return self.parse_encoders(ret)

	def get_state(self):
		cmd = self.cmd_get_state
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(10)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 10
		return self.parse_state(ret)


	def get_distances(self):
		cmd = self.cmd_get_distances
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(7)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 7
		return self.parse_distances(ret)
	
	def __init__(self, port = None):
		if port != None:
			self.port = port
		else:
			raise Exception('port is None')

		self.state = self.get_state()
		
if __name__ == "__main__":
	from biu import BIU
	khc = KHC(BIU())
	print(khc.get_distances())
	# print(khc.gooo(31))
	# sleep(6)
	# print(khc.gooo(-31))
	# sleep(6)
	print(khc.stop_engine())
