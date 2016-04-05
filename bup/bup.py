import sys
from serial import Serial, SerialException

try:
	import bup.configuration as configuration
except ImportError:
	import configuration as configuration

class BUP(Serial):
	state = dict()
	def get_my_port(self, open_ports = []):
		ports = configuration.PORTS
		for port in open_ports:
			ports.remove(port)
		for p in configuration.PORTS:
			try:
				print('Trying port %s ...' % p, end = '', file = sys.stderr)
				s = Serial(port = p, baudrate = configuration.BAUDRATE, timeout = 0.1)
				if s.read(10) != b'': raise SerialException('wrong port, unexpected data')
				self.state = {}
				print(' ok, ', end = '', file = sys.stderr)
				for bupname in configuration.BUP_QUERY.keys():
					print('trying bup %s ' % bupname, end = '', file = sys.stderr)
					q = configuration.BUP_QUERY[bupname]['q']
					a = configuration.BUP_QUERY[bupname]['a']
					s.write(q)
					if len(s.readall()) == a: 
						present = True
						print('ok', file = sys.stderr)
					else:
						present = False
						print('none', file = sys.stderr)
					self.state.update({
						bupname : dict(present = present)
					})
				if self.state['kup']['present']: return p
			except SerialException as e:
				print(e, file = sys.stderr)
		return None

	def __init__(self, open_ports = []):
		try:
			super().__init__(
				port     = self.get_my_port(open_ports),
				timeout  = configuration.TIMEOUT,
				baudrate = configuration.BAUDRATE,
			)
		except Exception as e:
			raise e


if __name__ == "__main__":
	bup = BUP()
	print(bup.state)
	bup.write(b'\xae\xae\xbb\x00\x04\x07\x00')
	print(bup.readall())
	bup.write(b'\xae\xae\xbb\x00\x10\x07\x00')
	print(bup.readall())
	bup.write(b'\xae\xae\xbb\x00\x01\x07\x00')
	print(bup.readall())
	# bup.write(b'\xae\xae\xbb\x00\x20\x07\x00')
	# print(bup.readall())
	# bup.write(b'\xae\xae\xbb\x00\x02\x07\x00')
	# print(bup.readall()) 
