import sys
from serial import Serial, SerialException

try:
	import biu.configuration as configuration
except ImportError:
	import configuration as configuration

class BIU(Serial):
	state = dict()
	def get_my_port(self):
		for p in configuration.PORTS:
			try:
				print('Trying port %s ...' % p, end = '', file = sys.stderr)
				s = Serial(port = p, baudrate = configuration.BAUDRATE, timeout = 0.1)
				if s.read(10) != b'': raise SerialException('wrong port, unexpected data')
				self.state = {}
				print(' ok, ', end = '', file = sys.stderr)
				for biuname in configuration.BIU_QUERY.keys():
					print('trying biu %s ' % biuname, end = '', file = sys.stderr)
					q = configuration.BIU_QUERY[biuname]['q']
					a = configuration.BIU_QUERY[biuname]['a']
					s.write(q)
					if len(s.readall()) == a: 
						present = True
						print('ok', file = sys.stderr)
					else:
						present = False
						print('none', file = sys.stderr)
					self.state.update({
						biuname : dict(present = present)
					})
				if self.state['kru']['present'] or \
				   self.state['khc']['present'] or \
				   self.state['ken']['present'] or \
				   self.state['kst']['present']	: return p
			except SerialException as e:
				print(e, file = sys.stderr)
		return None

	def __init__(self):
		try:
			super().__init__(
				port     = self.get_my_port(),
				timeout  = configuration.TIMEOUT,
				baudrate = configuration.BAUDRATE,
			)
		except Exception as e:
			raise e


if __name__ == "__main__":
	biu = BIU()
	print(biu.state)
	biu.write(b'\xae\xae\x01\x00\xff\x07\x00')
	print(biu.readall())