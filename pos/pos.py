from math import *

# try:
# 	from student import *
# except:
# 	from pos.student import *

class Position(object):
	NAME = 'POSITION'

	def radtomx(self, a = 0, c = 0):
		c = degrees(c)
		n = (6 + c) / 6
		l0 = (c - (3 + 6 * (n - 1))) / 57.29577915
		x1 = pow(l0, 2) * (109500 - 574700 * sin(a) * sin(a) + 863700 * pow(sin(a), 4) - 398600 * pow(sin(a), 6))
		x2 = l0 * l0 * (278194 - 830174 * pow(sin(a), 2) + 572434 * pow(sin(a), 4) - 16010 * pow(sin(a), 6) + x1)
		x3 = l0 * l0 * (672483.4 - 811219.9 * pow(sin(a), 2) + 5420 * pow(sin(a), 4) - 10.6 * pow(sin(a), 6) + x2)
		x4 = l0 * l0 * (1594561.25 + 5336.535 * pow(sin(a), 2) + 26.79 * pow(sin(a), 4) + .149 * pow(sin(a), 6) + x3)
		x = 6367558.4968 * a - sin(2 * a) * (16002.89 + 66.9607 * pow(sin(a), 2) + .3515 * pow(sin(a), 4) - x4)
		return x

	def radtomy(self, a = 0, c = 0):
		c = degrees(c)
		n = (6 + c) / 6
		l = (c - (3 + 6 * (n - 1))) / 57.29577915;
		y = 1E5 * (5 + 10 * n) + \
			l * cos(a) * (
				6378245 + 21346.1415 * pow(sin(a), 2) + 
				107.159 * pow(sin(a), 4) + 
				0.5977 * pow(sin(a), 6) + 
				l * l * (
					1070204.16 - 2136826.66 * pow(sin(a), 2) + 
					17.98 * pow(sin(a), 4) - 11.99 * pow(sin(a), 6) + 
					l * l * (
						270806 - 1523417 * pow(sin(a), 2) + 
						1327645 * pow(sin(a), 4) - 21701 * pow(sin(a), 6) + 
						l * l * (
							79690 - 866190 * pow(sin(a), 2) + 1730360 * pow(sin(a), 4) - 945460 * pow(sin(a), 6)
					)
				)
			)
		)
		return y

	def setCurrentPosition(self, x = 0, y = 0, bins = None):
		if bins:
			_ = self.bins.get_state()
			self.x0 = self.radtomx(_['Lat_bins'],_['Lon_bins'])
			self.y0 = self.radtomy(_['Lat_bins'],_['Lon_bins'])
		else:
			self.x0 = x
			self.y0 = y

	def get_state(self):
		if self.bins:
			_ = self.bins.get_state()
			self.x = self.x0 - self.radtomx(_['Lat_bins'],_['Lon_bins'])
			self.y = self.y0 - self.radtomy(_['Lat_bins'],_['Lon_bins'])
		else:
			self.x = 0
			self.y = 0

		return dict(x = self.x, y = self.y)

	def __init__(self, bins = None, cv = None, rfind = None, odo = None):
		self.bins = bins
		self.cv = cv
		self.rfind = rfind
		self.odo = odo
		assert self.bins != None or self.cv != None or self.rfind != None or self.odo != None
		if self.bins:
			self.setCurrentPosition(bins = self.bins)
		else:
			self.setCurrentPosition(x = 0, y = 0)
		
if __name__ == "__main__":
	x0 = radtomx(1.01324277,0.9812698)
	y0 = radtomy(1.01324277,0.9812698)
	x1 = radtomx(1.0132427800000001,0.98126972)
	y1 = radtomy(1.0132427800000001,0.98126972)
	print(x1-x0, y1-y0)
