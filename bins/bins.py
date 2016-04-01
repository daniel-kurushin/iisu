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

D70 = dict(
	signature = (b'\x37', b'\x70'),
)

D33 = dict(
	signature = (56, 162),
	C = 0.0, T = 0.0, R = 0.0,
	C0 = 0, T0 = 0, R0 = 0,
	Ax = 0.0, Ay = 0.0, Az = 0.0,
	Wx = 0.0, Wy = 0.0, Wz = 0.0,
	t = datetime.datetime.now().__str__()
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

	def send_packet(packet_id, data):
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
	
	def parse_packet_70h(self, packet_bytes):
			
		data = {}
		
		data['acceleration'] = \
			unpack("<f", packet_bytes[4:8])[0], \
				unpack("<f", packet_bytes[8:12])[0], \
				unpack("<f", packet_bytes[12:16])[0]
				
		data['angular_velocity'] = \
			unpack("<f", packet_bytes[16:20])[0], \
				unpack("<f", packet_bytes[20:24])[0], \
				unpack("<f", packet_bytes[24:28])[0]
				
		data['orientation'] = \
			unpack("<f", packet_bytes[32:36])[0], \
				unpack("<f", packet_bytes[28:32])[0], \
				unpack("<f", packet_bytes[36:40])[0]
				
		data['position'] = \
			unpack("<i", packet_bytes[40:44])[0] / 10 ** 8, \
				unpack("<i", packet_bytes[44:48])[0] / 10 ** 8, \
				unpack("<f", packet_bytes[48:52])[0]
				
		data['time'] = datetime.datetime.now()
				
		return data

	def read_packets(self):
		print('start reading', file = sys.stderr)
		while not self.end and \
			self.state['errorcount'] < self.MAX_ERROR_COUNT:

			T0 = datetime.datetime.now()

			if self.read_synchro():
				pln, sig = self.read_signature()
				if (pln, sig) == D70['signature']: 
					D70.update(self.parse_packet_70h(self.read(ord(pln))))
				elif sig == D33['signature']: 
					pass
					# read33packet()
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
	for x in range(10):
		sleep(10)
		print(D70)
	print(bins.stop())


# exit(0)




# import datetime
# import json
# import struct
# import time
# import threading
# import math
# import sys
# import serial
# # from filter import DriftFilter, DriftFilterParameters
# from crc import *

# CMD = "170"
# HOST = "1"
# ZERO_IS_SET = "4"
# ROTO_IS_READY = "5"

# c = 0
# t = 0

# loop = True

# D70 = dict(
# 	signature=55,  # (55, 112)
# 	C=0.0, T=0.0, R=0.0,
# 	C0=0, T0=0, R0=0,
# 	Ax=0.0, Ay=0.0, Az=0.0,
# 	Wx=0.0, Wy=0.0, Wz=0.0,
# 	t=datetime.datetime.now().__str__()
# )

# def open_bins_port():
# 	global BINSport
# 	try:
# 		BINSport = serial.Serial(
# 			port='/dev/ttyUSB0',
# 			baudrate=460800,
# 			parity='N',
# 			stopbits=1,
# 			bytesize=8,
# 			timeout=1,
# 		)
# 	except (FileNotFoundError, serial.serialutil.SerialException) as e:
# 		BINSport = None

# def read70packet(self, echo=True):
# 	global initial_time_70, last_time_70
# 	global x, y, z
# 	global vx, vy, vz
# 	global last_log_time_70

# 	crc = ord(BINSport.read())
# 	BINSport.read(4)
# 	D70['Ax'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Ay'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Az'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Wx'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Wy'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Wz'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['R'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['C'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['T'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['Lat'] = struct.unpack('<i', BINSport.read(4))[0]
# 	D70['Lon'] = struct.unpack('<i', BINSport.read(4))[0]
# 	D70['H'] = struct.unpack('<f', BINSport.read(4))[0]
# 	D70['t'] = datetime.datetime.now().__str__()

# 	f = open('log.dat', 'a')
# 	f.write("%s %s\n" % (D70['t'], D70['C']))
# 	f.close()

# 	if D70['C'] > 180:
# 		D70['C'] -= 360


# def ask_packet(packet_id, packet_frequency):
# 	request  = b"\x40\x00"
# 	request += packet_id.to_bytes(length = 1, byteorder = "little")
# 	request += packet_frequency.to_bytes(length = 4, byteorder = "little",)
# 	crc = compute_crc(request)
	
# 	request  = b"\xAA\xAA\x09" + request
# 	request += crc.to_bytes(length = 2, byteorder = "little")
		
# 	print(''.join(["%02x " % x for x in request]))
# 	# AA AA 09 40 00 4C 64 00 00 00 8C D4
# 	# aa aa 09 40 00 4c 0a 00 00 00 04 2f
# 	BINSport.write(request)

# def send_packet(packet_id, data):
# 	# return #!!!!!
# 	if not 0 <= packet_id <= 255:
# 		raise Exception() #!!!!!
		

# 	len_pack = len(data)*4 + 3

# 	request = packet_id.to_bytes(length = 1, byteorder = "little")

# 	for elem in data:
# 		if type(elem) == float:
# 			request += \
# 				struct.pack('<f', elem)
# 		elif type(elem) == int:
# 			request += \
# 				struct.pack('<i', elem)
# 		else:
# 			pass

# 	crc = compute_crc(request)
# 	request  = b"\xAA\xAA" + len_pack.to_bytes(length = 1, byteorder = "little") + request + crc.to_bytes(length = 2, byteorder = "little")

# 	# "\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
# 		# AA AA 17 45 40 A3 08 06 CD C3 D9 05 B4 00 00 00 64 00 00 00 05 00 00 00 F5 8D
# 	# b'\xaa\xaa\x0b@p\x00\x00\x00\x00\x00\x00\x00\xd5\xef'
# 	#     aa  aa  08
# 	# aa aa 07 4d 00 00 00 00 12 30
# 	# AA AA 07 4D 00 00 61 45 68 10
# 	print(''.join(["%02x " % x for x in request]))

# 	BINSport.write(request)

# def list_packets(n = 0):
# 	global loop
# 	sync = 170  # AAh
# 	if n != 0:
# 		loop = False
# 		k = n
# 	else:
# 		loop = True
# 		k = 0
# 	while loop or k > 0:
# 		if k > 0:
# 			k -= 1
# 		T0 = datetime.datetime.now()
# 		try:
# 			while 1:
# 				if ord(BINSport.read()) == sync:
# 					if ord(BINSport.read()) == sync:
# 						break

# 			x = ord(BINSport.read())
# 			print(x,ord(BINSport.read()))

# 		except AttributeError as e:
# 			pass
# 		except TypeError as e:
# 			pass


# def read_packet(n = 0):
# 	sync = 170  # AAh
# 	if n != 0:
# 		loop = False
# 		k = n
# 	else:
# 		loop = True
# 		k = 0
# 	while loop or k > 0:
# 		if k > 0:
# 			k -= 1
# 		T0 = datetime.datetime.now()
# 		try:
# 			while 1:
# 				if ord(BINSport.read()) == sync:
# 					if ord(BINSport.read()) == sync:
# 						break

# 			test_byte = ord(BINSport.read())
# 			if test_byte == D70['signature']:  # (ord(BINSport.read()),ord(BINSport.read())) == D70.signature:
# 				read70packet(self, echo=False)

# 		except AttributeError as e:
# 			pass
# 		except TypeError as e:
# 			pass


# if __name__ == "__main__":    
# 	open_bins_port()
# 	ask_packet(0x70,1)
# 	time.sleep(10)
# 	read_packet(1)
# 	print(D70)
# 	# threading.Thread(target=read_packet).start()


