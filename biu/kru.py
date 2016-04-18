import sys
from struct import pack, unpack
from time import sleep

class KRU(object):
	NAME = 'KRU'

	BOTH = 2
	LEFT = 0
	RIGHT = 1

	OO__OO__ = 0
	OOO_OOO_ = 1
	O___O___ = 2

	IS_FLK_ON = 0

	cmd_steer      = b'\xae\xae\x02\x00\x01\x08\x00' # повернуть в поз хх
	cmd_get_pos    = b'\xae\xae\x02\x00\x02\x07\x00' # вернуть текущее положение
	cmd_flick      = b'\xae\xae\x02\x00\x03\x09\x00' # включить указатели поворота
													 # сторона: 0х00 левый
													 #          0х01 правый
													 #		    0х02 оба
													 # режим:   0х00 поворот       --__--__--
													 #          0х01 затмевание    ---_---_--
													 #          0х02 проблеск      -___-___-	
	cmd_stop_flick = b'\xae\xae\x02\x00\x04\x07\x00' # отключить указатели поворота
	cmd_restart    = b'\xae\xae\x02\x00\x05\x07\x00' # перезапустить машину состояний
	cmd_get_state  = b'\xae\xae\x02\x00\xff\x07\x00' # вернуть состояние КРУ
													 # currentRudderPos
													 # targetRudderPos
													 # minRudderPos
													 # maxRudderPos
													 # mdlRudderPos
													 # rudderState
													 # LIM_RIGHT
													 # LIM_LEFT
													 # flickersMode
													 # flickerState
													 # flk_onTime
													 # flk_offTime

	def parse_flickers_state(self, x):
		return dict(
			ok = True,
			flickersMode = unpack('<b', x[3:4])[0],
			flickerState = unpack('<b', x[4:5])[0],
			flk_onTime = unpack('<b', x[5:6])[0],
			flk_offTime = unpack('<b', x[6:7])[0],
			flk_on = self.IS_FLK_ON,
		)

	def parse_steer_res(self, x):
		return dict(
			ok = x[3:4] == b'\xff',
			pos = unpack('<b', x[4:5])[0],
		)

	def parse_steer_pos(self, x):
		return dict(
			ok = True,
			pos = unpack('<b', x[3:4])[0],
		)

	def parse_state(self, x):
		return dict(
			ok = True,
			currentRudderPos = unpack('<b', x[3:4])[0],
			targetRudderPos = unpack('<b', x[4:5])[0],
			minRudderPos = unpack('<b', x[5:6])[0],
			maxRudderPos = unpack('<b', x[6:7])[0],
			mdlRudderPos = unpack('<b', x[7:8])[0],
			rudderState = unpack('<b', x[8:9])[0],
			LIM_RIGHT = unpack('<b', x[9:10])[0],
			LIM_LEFT = unpack('<b', x[10:11])[0],
			flickersMode = unpack('<b', x[11:12])[0],
			flickerState = unpack('<b', x[12:13])[0],
			flk_onTime = unpack('<b', x[13:14])[0],
			flk_offTime = unpack('<b', x[14:15])[0],
	)

	def steer(self, pos = 0):
		cmd = self.cmd_steer
		pos = pack('>b', pos)
		print('>>>', cmd, pos, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(pos)
		ret = self.port.read(5)
		print('<<<', ret, file = sys.stderr)
		sleep(.5)
		assert len(ret) == 5
		return self.parse_steer_res(ret)

	def get_pos(self):
		cmd = self.cmd_get_pos
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		return self.parse_steer_pos(ret)

	def flick(self, side = BOTH, mode = OO__OO__):
		cmd = self.cmd_flick
		side = pack('>b', side)
		mode = pack('>b', mode)
		print('>>>', cmd, side, mode, file = sys.stderr)
		self.port.write(cmd)
		self.port.write(side)
		self.port.write(mode)
		ret = self.port.read(7)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 7
		self.IS_FLK_ON = 1
		return self.parse_flickers_state(ret)

	def stop_flick(self):
		cmd = self.cmd_stop_flick
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(7)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 7
		self.IS_FLK_ON = 0
		return self.parse_flickers_state(ret)

	def restart(self):
		cmd = self.cmd_restart
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(4)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 4
		self.IS_FLK_ON = 0
		return self.get_state()

	def get_state(self):
		cmd = self.cmd_get_state
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(15)
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 15
		return self.parse_state(ret)

	def __init__(self, port = None):
		if port != None:
			self.port = port
		else:
			raise Exception('port is None')


if __name__ == "__main__":
	from biu import BIU
	kru = KRU(BIU())
	print(kru.steer(-20))
	print(kru.get_pos())
	print(kru.steer(0))
	print(kru.get_pos())
	print(kru.steer(20))
	print(kru.get_pos())
	print(kru.steer(0))
	print(kru.get_pos())
	print(kru.steer(-5))
	print(kru.get_pos())
	print(kru.steer(-2))
	print(kru.get_pos())
	print(kru.steer(0))
	print(kru.get_pos())
	print(kru.steer(2))
	print(kru.get_pos())
	print(kru.steer(0))
	print(kru.get_pos())
