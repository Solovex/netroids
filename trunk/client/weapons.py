import math, random
from base_class import *
from particles import *

class rocketWeapon(baseWeapon):
	def __init__(self, pMgr, start, rot):
		baseWeapon.__init__(self, start, rot, 100, pMgr)
		self.width, self.height = 2, 10
		self.wire = [[-self.width, -self.height] , [self.width, -self.height], [self.width, self.height], [-self.width, self.height]] #pocisk

		self.vect = 1
		self.speed_up = 15 #wzrost predkosci
		self.setSpeed()
		

	def setSpeed(self):
		self.speed = map(lambda x: -x, [self.vect*math.cos(self.rot+math.pi/2), self.vect*math.sin(self.rot+math.pi/2)])

	def update(self):
		baseWeapon.update(self)
		spaliny = self.speed_up-self.ticks
		if self.ticks >= self.speed_up:
			self.vect = (self.ticks/10) ** 2
			self.setSpeed()
			spaliny = 3
		map(lambda p: self.pos.__setitem__(p, self.pos.__getitem__(p) + self.speed.__getitem__(p)), range(2))
		
		for i in range(spaliny):
			self.pMgr.addNew(particleRocket(map(lambda x: x+random.randint(-2,2), self.pos[:]), map(lambda x: -x, self.speed[:])))

	def draw(self, widok, pos):
		pts = []
		for i in range(len(self.wire)):
			pts.append([ pos[0] + self.wire[i][0] * math.cos(self.rot) - self.wire[i][1] * math.sin(self.rot), pos[1] + self.wire[i][0] * math.sin(self.rot) + self.wire[i][1] * math.cos(self.rot)])
		pygame.draw.polygon(widok, (255, 255, 255), pts)
	def hit(self):
		for i in range(random.randint(3,10)):
			self.pMgr.addNew(particleExplosion(map(lambda x: x+random.randint(-15,15), self.pos[:]), [0,0]))
