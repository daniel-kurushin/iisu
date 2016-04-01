import json
import sys

from math import *

from biu import BIU
from kru import KRU
from khc import KHC

class Movement:
	port = None
	kru  = None
	khc  = None
	bup  = None
	bins = None

	def ask_position(self, arg):
		pass

	def ask_permission(self, arg):
		pass

	def is_ok_to_go(self, *args, **kwargs):
		pass

	def qcheck(self, *args, **kwargs):
		pass

	def ask_permission(self, *args, **kwargs):
		pass

	def calc_trajectory(self, *args, **kwargs):
		for x in kwargs.keys():
			arg = kwargs[x]
			if   x == 'point': points = self.curve_from_point(arg); break
			else:
				raise Exception('impossible to calc')

		print(points)

	def curve_from_point(self, arg):
		dX, dY = arg['dX'], arg['dY']
		x0, y0 = dX / 2, dY / 2
		b = -(-dX/dY * x0 - y0)
		xC = b * dY / dX

		print(dX, dY, x0, y0, b, xC)

		points = {}
		R = xC
		D = dX / 10
		x = 0
		for i in range(10):
			try:
				y = sqrt(-x * (x - 2 * R))
			except ValueError:
				y = 0
			
			points.update({i:(round(x,2),round(y,2))})
			x += D

		points.update({10:(round(dX,2),round(dY,2))})
		return points


	def go_point(self, arg):
		pass

	def go_time_dir(self, arg):
		pass

	def go_speed_dir(self, arg):
		pass

	def go_curve(self, arg):
		pass


	def go(self, *args, **kwargs):
		if self.is_ok_to_go(
			internal = self.qcheck(self.khc, self.kru, self.bup, self.bins),
			external = self.ask_permission(
					trajectory = self.calc_trajectory(**kwargs)
				)
			):
			for x in kwargs.keys():
				arg = kwargs[x]
				if   x == 'point': self.go_point(arg); break
				elif x == 'time_dir': self.go_time_dir(arg); break
				elif x == 'speed_dir' : self.go_speed_dir(arg); break
				elif x == 'curve': self.go_curve(arg); break
				else:
					raise Exception('impossible to move')
		else:
			raise Exception('impossible to move')


	def __init__(self, port = None):
		if port != None:
			self.port = port
			self.kru = KRU(port)
			self.khc = KHC(port)
		else:
			raise Exception('port is None')


if __name__ == "__main__":
	m = Movement(BIU())
	m.go(point     = dict(dX = -1, dY =  1)) # m, m
	m.go(point     = dict(dX =  1, dY = -1)) # m, m
	m.go(time_dir  = dict(dT = 10,  A =  0)) # s, rad
	m.go(speed_dir = dict(dT = 10,  V =  1)) # s, m/s
	m.go(curve     = dict( L =  1,  R =  3)) # m, m
	m.go(curve     = dict( L = -1,  R = -4)) # m, m