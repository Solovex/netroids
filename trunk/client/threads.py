import pygame
import struct
import random, math
from threading import Thread

class gameThread(Thread):
	def __init__(self, screen):
		Thread.__init__(self)
		self.zegar=pygame.time.Clock()
		self.parent = screen
		self.pingtick = 0
		self.tick = 0
		self.time, self.ping = 0, 0
		self.running = False
	def __del__(self):
		self.running = False
		self.join()
	def run(self):
		self.running = True
		while self.running:
 
			if self.parent.reading != True:
				for i in self.parent.statki:
					self.parent.statki[i].update()
			self.pingtick += 1
			self.tick += 1
			if self.pingtick > 50:
				self.parent.parent.client.send(struct.pack('3i', 3, self.tick, random.randint(0,65535)))
				self.pingtick = 0
			self.parent.particleManager.updateAll()
			self.parent.weaponManager.updateAll()
			self.zegar.tick(50)
