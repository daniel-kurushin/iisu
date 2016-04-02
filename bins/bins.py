import sys
import datetime
import json
import math

from struct import pack, unpack
from serial import Serial, SerialException
from threading import Thread
from time import sleep



try:
	import bins.configuration as configuration
	from bins.crc import compute_crc
except ImportError:
	import configuration as configuration
	from crc import compute_crc

D33 = dict(
	signature = (b'\x53', b'\x33'),
)

D35 = dict(
	signature = (b'\x47', b'\x35'),
)

D70 = dict(
	signature = (b'\x37', b'\x70'),
)

class BINS(Serial):
	name = 'BINS'

	MAX_ERROR_COUNT = 100

	state = dict(
		errorcount = 0,
	)

	def read_synchro(self):
		if self.read() == configuration.SYNCHRO:
			if self.read() == configuration.SYNCHRO:
				return True
		return False

	def read_signature(self):
		return self.read(), self.read()


	def ask_packet_new(self, bins_serial = None, packet_id = 0x70, packet_frequency = 100, type_of_protocol = None):
		if not 0 <= packet_id <= 255:
			raise Exception() #!!!!!

		if not 0 <= packet_frequency <= 1000:
			raise Exception() #!!!!!


		request  = b"\x40"
		if type_of_protocol != None:
			request += type_of_protocol.to_bytes(length = 1, byteorder = "little")

		request += packet_id.to_bytes(length = 1, byteorder = "little")
		request += \
			(packet_frequency // 10).to_bytes(
				length    = 4,
				byteorder = "little",
			)
		crc = compute_crc(request)

		request  = b"\xAA\xAA\x09" + request
		request += crc.to_bytes(length = 2, byteorder = "little")

		bins_serial.write(request)



	def get_my_port(self):
		for p in configuration.PORTS:
			try:
				print('Trying port %s ... ' % p, end = '', file = sys.stderr)
				s = Serial(port = p, baudrate = configuration.BAUDRATE, timeout = 0.1)
				n = 0
				while 1:
					if s.read() == configuration.SYNCHRO:
						if s.read() == configuration.SYNCHRO:
							print('success!', file = sys.stderr)
							return p
					elif s.read() == b'':
						raise SerialException('Wrong data on port %s' % p)
					else: n += 1
					if n > configuration.MAX_PACKET_LENGTH:
						raise SerialException('Wrong data on port %s' % p)
			except SerialException as e:
				print(e, file = sys.stderr)
		return None

	def list_packets(self, n = 0):
		res = {}
		while n > 0:
			if self.read_synchro():
				pln, sig = self.read_signature()
				res.update({hex(ord(sig)):{'present': True, 'len': ord(pln)}})
				n -= 1

		return res

	def send_packet(self, packet_id, data):
		# return #!!!!!
		if not 0 <= packet_id <= 255:
			raise Exception() #!!!!!
			

		len_pack = len(data)*4 + 3

		request = packet_id.to_bytes(length = 1, byteorder = "little")

		for elem in data:
			if type(elem) == float:
				request += \
					struct.pack('<f', elem)
			elif type(elem) == int:
				request += \
					struct.pack('<i', elem)
			else:
				pass

		crc = compute_crc(request)
		request  = b"\xAA\xAA" + len_pack.to_bytes(length = 1, byteorder = "little") + request + crc.to_bytes(length = 2, byteorder = "little")

		# "\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
			# AA AA 17 45 40 A3 08 06 CD C3 D9 05 B4 00 00 00 64 00 00 00 05 00 00 00 F5 8D
		# b'\xaa\xaa\x0b@p\x00\x00\x00\x00\x00\x00\x00\xd5\xef'
		#     aa  aa  08
		# aa aa 07 4d 00 00 00 00 12 30
		# AA AA 07 4D 00 00 61 45 68 10
		print(''.join(["%02x " % x for x in request]))

		BINSport.write(request)

	def make_packet(self, packet_data = {}):
		ordered = [0] * len(packet_data.keys())
		print(ordered)
		for key, val in packet_data.items():
			n = val[0] - 1
			F = val[1]
			K = val[2]
			D = val[3]
			ordered[n] = pack(F, D * K)

		return ordered
	
	def parse_packet(self, packet_id, packet_bytes):
		data = {}
		for key, val in configuration.packets_in[packet_id].items():
			F = val[1]
			L = len(pack(F,0))
			d0, d1 = (val[0] - 1) * L, (val[0] - 1) * L + L
			K = val[2]
			data[key] = unpack(F, packet_bytes[d0:d1])[0] * K
		
		return data

	def read_packets(self):
		print('start reading', file = sys.stderr)
		while not self.end and \
			self.state['errorcount'] < self.MAX_ERROR_COUNT:

			T0 = datetime.datetime.now()

			if self.read_synchro():
				pln, sig = self.read_signature()
				if (pln, sig) == D70['signature']: 
					D70.update(self.parse_packet('p70h',self.read(ord(pln))))
				elif (pln, sig) == D33['signature']: 
					D33.update(self.parse_packet('p33h',self.read(ord(pln))))
				elif (pln, sig) == D35['signature']: 
					D35.update(self.parse_packet('p35h',self.read(ord(pln))))
				elif sig == 0:
					self.state


		print('stop reading', file = sys.stderr)

	def stop(self):
		self.end = True
		self.reader.join()


	def __init__(self):
		try:
			super().__init__(
				port     = self.get_my_port(),
				timeout  = configuration.TIMEOUT,
				baudrate = configuration.BAUDRATE,
				parity   = configuration.PARITY,
				stopbits = configuration.STOPBITS,
				bytesize = configuration.BYTESIZE,
			)

			self.end = False

			self.state.update(self.list_packets(20))

			self.reader = Thread(target = self.read_packets)
			self.reader.start()
		except Exception as e:
			raise e

if __name__ == "__main__":
	bins = BINS()
	print(bins.state)
	x = configuration.packets_out['p40h']
	x['Type'][3] = 1
	x['PkID'][3] = 1
	x['Freq'][3] = 1
	print(bins.make_packet(x))
	for x in range(2):
		sleep(10)
		print(D70)
		print(D33)
		print(D35)
	print(bins.stop())