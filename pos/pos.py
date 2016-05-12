from math import *

try:
	from student import *
except:
	from pos.student import *

class Position(object):
	NAME = 'POSITION'
	xₒ = 0
	yₒ = 0
	Δx = 0
	Δy = 0

	def radtomx(self, a = 0, c = 0):
		c = degrees(c)
		n = (6 + c) / 6
		lₒ = (c - (3 + 6 * (n - 1))) / 57.29577915
		x1 = pow(lₒ, 2) * (109500 - 574700 * sin(a) * sin(a) + 863700 * pow(sin(a), 4) - 398600 * pow(sin(a), 6))
		x2 = lₒ * lₒ * (278194 - 830174 * pow(sin(a), 2) + 572434 * pow(sin(a), 4) - 16010 * pow(sin(a), 6) + x1)
		x3 = lₒ * lₒ * (672483.4 - 811219.9 * pow(sin(a), 2) + 5420 * pow(sin(a), 4) - 10.6 * pow(sin(a), 6) + x2)
		x4 = lₒ * lₒ * (1594561.25 + 5336.535 * pow(sin(a), 2) + 26.79 * pow(sin(a), 4) + .149 * pow(sin(a), 6) + x3)
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

	def setCurrentPosition(self, x = [], y = []):
		try:
			Xₛ,Yₛ = Student(x,0.95), Student(y,0.95)
			self.x, self.y = Xₛ.X, Yₛ.X
			self.Δx, self.Δy = Xₛ.Dx, Yₛ.Dx
		except NotEnoughValuesException:
			try:
				self.x, self.y = x[0], y[0]
			except IndexError:
				self.x, self.y = self.xₒ, self.yₒ

	def setInitialPosition(self, x = 0, y = 0, bins = None):
		if bins:
			_ = self.bins.get_state()
			self.xₒ = self.radtomx(_['Lat_bins'],_['Lon_bins'])
			self.yₒ = self.radtomy(_['Lat_bins'],_['Lon_bins'])
		else:
			self.xₒ = x
			self.yₒ = y

	def xy_from_bins(self):
		return 0,0

	def dxy_from_biu(self):
		return 0,0

	def dxy_from_cv(self):
		return 0,0

	def get_state(self):
		if self.bins:
			_ = self.bins.get_state()
			self.x = self.xₒ - self.radtomx(_['Lat_bins'],_['Lon_bins'])
			self.y = self.yₒ - self.radtomy(_['Lat_bins'],_['Lon_bins'])
		else:
			self.x = 0
			self.y = 0

		return dict(x = self.x, Δx = self.Δx, y = self.y, Δy = self.Δy)

	def __init__(self, bins = None, cv = None, khc = None, kru = None):
		self.bins = bins
		self.cv = cv
		self.khc = khc
		self.kru = kru
		assert self.bins != None or self.cv != None or self.khc != None or self.kru != None
		if self.bins:
			self.setInitialPosition(bins = self.bins)
		else:
			self.setInitialPosition(x = 0, y = 0)

	def __str__(self):
		return "%s±%s, %s±%s" % (round(self.x, 4), round(self.Δx, 4), round(self.y, 4), round(self.Δy, 4))
		
if __name__ == "__main__":
	p = Position(None, 1, 2, 3)
	p.setCurrentPosition([2,2,2],[4,3,2])
	print(p)
