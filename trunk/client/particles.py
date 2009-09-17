import random
from base_class import *
 
class particleEngine(baseParticle):
	def __init__(self,pos=[300,300],speed=[0,0]):
		baseParticle.__init__(self, pos, 100)
		self.speed = speed[:]
		self.width = 0
		
	def update(self):
		baseParticle.update(self)
		
		self.pos[0]+=self.speed[0]
		self.pos[1]+=self.speed[1]
		if self.ticks < 50:
			self.width = 10-(self.ticks / 5)
		else:
			self.width =0 
			
        def draw(self,widok, pos):
                c=120-self.ticks
                color = (c, c, c)
                if self.width <= 1:
                        widok.set_at(pos,color)
                else:
                        width = self.width / 2
                        x, y = (pos[0] - width), (pos[1] - width)
                        widok.fill(color, (x, y,  self.width, self.width))

class particleRocket(baseParticle):
        def __init__(self, pos=[300,300], speed=[0,0]):
                baseParticle.__init__(self, pos, random.randint(20, 50))
                self.speed = (random.random() * (-1 if random.randint(0,2) == 1 else 1), random.random() * (-1 if random.randint(0,2) == 1 else 1))
                
        def update(self):
                baseParticle.update(self)
                self.pos[0]+=self.speed[0]
                self.pos[1]+=self.speed[1]
        def draw(self, widok, pos):
                x=[(self.lifetime*1.5)-self.ticks] * 3
                widok.fill(x, (pos[0], pos[1], 1, 1)) #zamiast set_at

class baseExplosionParticle(baseParticle):
	def __init__(self, pos, speed, max_r):
		baseParticle.__init__(self, pos, max_r)
		#self.x, self.y = (0, 0)
		self.start = pos[:]
		self.w = 0
		self.max_r = max_r
		self.clr_base = (random.randint(127,255), random.randint(0,127))
		self.clr = [x for x in self.clr_base[:]]
		self.step = self.lifetime
	def update(self):
		baseParticle.update(self)
		self.w = self.ticks + 1
	def draw(self, widok, pos):
		x, y = self.start[0] - self.w, self.start[1] - self.w
		rect = (pos[0]-self.w, pos[1]-self.w, self.w*2,self.w*2)
		self.clr[0] -= self.clr_base[0]/self.step
		self.clr[1] -= self.clr_base[1]/self.step
		self.clr=[0 if x<0 else x for x in self.clr]
		
		color = (self.clr[0], self.clr[1], 0)
		pygame.draw.ellipse(widok, color, rect)

class particleExplosion(baseExplosionParticle):
	def __init__(self, pos, speed):
		baseExplosionParticle.__init__(self, pos, speed, random.randint(1,5)*10)
