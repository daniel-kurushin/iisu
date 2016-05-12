import sys
from struct import pack, unpack
from time import sleep
from threading import Thread
from time import sleep

class KUP(object):
	NAME  = 'BUP'
	state = {}
	_lock  = False

	cmd_measure = b'\xae\xae\xbb\x00\x04\x07\x00' # Измерение
										          # I_48 ток 48 в
										          # I_12 ток 12 в
										          # U_12 напряжение 12 в
	cmd_12v_on  = b'\xae\xae\xbb\x00\x02\x07\x00' # Вкл канал 12 в !!!!! обычно вкл !!!!!
										          # PIN_power_self
										          # PIN_power_12
										          # PIN_power_48
	cmd_12v_off = b'\xae\xae\xbb\x00\x20\x07\x00' # Выкл канал 12 в !!!!! Убивает все !!!!
										          # PIN_power_self
										          # PIN_power_12
										          # PIN_power_48
	cmd_48v_on  = b'\xae\xae\xbb\x00\x01\x07\x00' # Вкл канал 48 в (обычно вкл)
										          # PIN_power_self
										          # PIN_power_12
										          # PIN_power_48
	cmd_48v_off = b'\xae\xae\xbb\x00\x10\x07\x00' # Выкл канал 48 в (остановит двигатель)
										          # PIN_power_self
										          # PIN_power_12
										          # PIN_power_48

	def __lock(self):
		self._lock = True

	def __unlock(self):
		self._lock = False

	def __isLock(self):
		return self._lock

	def parse_measure(self, x):
		return dict(
			ok = True,
			I_48 = round(abs(int(unpack('<b', x[7: 8])[0]) * -0.3268 + 9.5376),2),
			I_12 = round(abs(int(unpack('<b', x[8: 9])[0]) * -0.3268 + 9.5376),2),
			U_12 = round(int(unpack('<B', x[9:10])[0]) * 0.0566,2),
		)
	
	def parse_state(self, x):
		return dict(
			ok = True,
			PIN_power_self = bool(unpack('<b', x[7: 8])[0]),
			PIN_power_48   = bool(unpack('<b', x[8: 9])[0]),
			PIN_power_12   = bool(unpack('<b', x[9:10])[0]),
		)


	def measure(self):
		while self.__isLock():
			sleep(.1)
		self.__lock()
		cmd = self.cmd_measure
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(100)
		self.__unlock()
		print('<<<', ret, len(ret), file = sys.stderr)
		assert len(ret) == 10
		return self.parse_measure(ret)

	def get_state(self):
		return self.state

	def do12v_on(self):
		while self.__isLock():
			sleep(.1)
		self.__lock()
		cmd = self.cmd_12v_on
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(10)
		self.__unlock()
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 10
		return self.parse_state(ret)

	def do12v_off(self):
		while self.__isLock():
			sleep(.1)
		self.__lock()
		cmd = self.cmd_12v_off
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(10)
		self.__unlock()
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 10
		return self.parse_state(ret) # Никогда ничего не вернет, если нет 
		                             # независимого питания ИИСУ тк
		                             # компьютер будет отключен!

	def do48v_on(self):
		while self.__isLock():
			sleep(.1)
		self.__lock()
		cmd = self.cmd_48v_on
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(10)
		self.__unlock()
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 10
		return self.parse_state(ret)

	def do48v_off(self):
		while self.__isLock():
			sleep(.1)
		self.__lock()
		cmd = self.cmd_48v_off
		print('>>>', cmd, file = sys.stderr)
		self.port.write(cmd)
		ret = self.port.read(10)
		self.__unlock()
		print('<<<', ret, file = sys.stderr)
		assert len(ret) == 10
		return self.parse_state(ret)

	def loop_measure(self):
		self.end = False
		print('BUP measures started', file = sys.stderr)
		while not self.end:
			if not self.__isLock():
				self.state.update(self.do12v_on())
				self.state.update(self.measure())
			sleep(10)
		print('BUP measures finished', file = sys.stderr)

	def finish(self):
		self.end = True
		self.measurer.join()

	def __init__(self, port = None):
		if port != None:
			self.port = port
			self.measurer = Thread(target = self.loop_measure)
			self.measurer.start()
		else:
			raise Exception('port is None')
		
if __name__ == "__main__":
	from bup import BUP
	kup = KUP(BUP())
	print(kup.get_state())
	sleep(10)
	print(kup.do48v_off())
	sleep(1)
	print(kup.get_state())
	print(kup.do48v_on())
	sleep(1)
	print(kup.get_state())
	kup.finish()
