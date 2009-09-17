import pygame, random, math
from particles import *

class spaceship():
	def __init__(self, pManager, pos=[300,300],id=0, name='',model=0):
		self.speed=[0,0]
		self.acc=[0,0]
		self.rot=0
		self.roting=0
		self.pos=pos
		self.wire=[[[-5,-10],[5,-10],[10,10],[-10,10]],
			  [[-20,-20],[20,-20],[20,20],[-20,20]]][model]
		self.speedchange=0
		self.rect=pygame.Rect(-5,-10,10,20)
		self.rect.size=(15,15)
		self.rect.center=self.pos
		self.name=name
		self.font = pygame.font.Font(None,15)
		self.id = id
		self.pManager = pManager

	def draw(self,widok, pos=[300,300]):
		for i in range(len(self.wire)):
			pygame.draw.aaline(widok,(255,255,255),
					(
						pos[0] + self.wire[i-1][0] * math.cos(self.rot) - self.wire[i-1][1] * math.sin(self.rot), #nigdy nie zrozumiem tych linijek wiec dodalem pare spacji i enterow zeby wygladaly na wazne
						pos[1] + self.wire[i-1][0] * math.sin(self.rot) + self.wire[i-1][1] * math.cos(self.rot)
					),
					(
						pos[0] + self.wire[i][0] * math.cos(self.rot) - self.wire[i][1] * math.sin(self.rot),
						pos[1] + self.wire[i][0] * math.sin(self.rot) + self.wire[i][1] * math.cos(self.rot)
					))

			rend = self.font.render("[%d] %s (%.1f, %.1f) (%.1f, %.1f)" % (self.id, self.name, self.pos[0], self.pos[1], self.speed[0], self.speed[1]), 0, (255,255,255))
			x= rend.get_rect()
			xx, yy = x[2], x[3]
			
			widok.blit(rend, (pos[0]-(xx/2), pos[1]+self.rect.size[1]))
		self.rect.center=self.pos
 
	def update(self):
		self.rot+=self.roting
		self.acc[0]=self.speedchange*math.cos(self.rot+math.pi/2)
		self.acc[1]=self.speedchange*math.sin(self.rot+math.pi/2)
		if self.speedchange:
			self.pManager.addNew(particleEngine([
					self.pos[0] + self.wire[2][0] * math.cos(self.rot)-self.wire[2][1] * math.sin(self.rot),
					self.pos[1] + self.wire[2][0] * math.sin(self.rot)+self.wire[2][1] * math.cos(self.rot)],
					( 5*self.acc[0]*random.random() , 5*self.acc[1] * random.random() ))) #lewy silnik

			self.pManager.addNew(particleEngine([
					self.pos[0]+self.wire[3][0]*math.cos(self.rot)-self.wire[3][1]*math.sin(self.rot),
					self.pos[1]+self.wire[3][0]*math.sin(self.rot)+self.wire[3][1]*math.cos(self.rot)],
					( 5 * self.acc[0] * random.random(), 5 * self.acc[1] * random.random())))
		self.speed[0]+=self.acc[0]
		self.speed[1]+=self.acc[1]
		self.pos[0]-=self.speed[0]
		self.pos[1]-=self.speed[1]
 

