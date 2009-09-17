import pygame, math

class baseParticle():
	def __init__(self, pos, lifetime):
		self.pos, self.lifetime = pos, lifetime
		self.ticks = 0
	def update(self):
		self.ticks += 1
		pass
	def draw(self, widok, pos):
		pass

class baseWeapon(baseParticle):
	def __init__(self, start, rot, distance_max, pMgr):
		baseParticle.__init__(self, start, 255)
		self.start = start[:]
		self.rot = rot
		self.distance_max = distance_max
		self.pMgr = pMgr
	def distance(self):
		return ( ((self.pos[0]-self.start[0]) ** 2) + ((self.pos[1]-self.start[1]) ** 2) ) ** 0.5
	def hit(self):
		pass

class baseScreen(): #bazowa klasa
	def __init__(self, surface):
		self.parent = surface
		self.surface = self.parent.wnd
		
	def updateScreen(self):
		pass
