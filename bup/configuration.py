PORTS	 = ['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
TIMEOUT  = 3
BAUDRATE = 9600

BUP_QUERY= dict(
	kup = dict(q = b'\xae\xae\xbb\x00\x00\x07\x00', a = 8),
)
