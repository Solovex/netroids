import pygame

class consoleLog():
	def __init__(self, return_callback):
		self.widok = pygame.Surface((600,200))
		self.widok.set_colorkey((0,0,0))
		self.log = ()
		self.font = pygame.font.Font(None,15)
		self.input_vis = False
		self.input = ""
		self.tick = 0
		self.return_callback = return_callback
	def add(self, what, color=(255,255,255)):
		self.log += (what,)
		self.repaint()
	def clear(self):
		self.log = ()
		self.repaint()
	def count(self):
		return len(self.log)
	def insert(self, index, text):
		self.log.insert(index, text)
		self.repaint()
	def repaint(self):
		self.widok.fill((0,0,0))
		c=0
		v=self.log[-12 if self.input_vis else -13:]
		for i in reversed(range(len(v))):
			y=(i*15)
			rend = self.font.render(v[i], 0, (255,255,255))
			self.widok.blit(rend, (0, y))
		if self.input_vis:
			rend = self.font.render(">>> %s%s" % (self.input, "" if self.tick <= 20 else "_"), 0, (255,255,255))
			self.widok.blit(rend, (0, 185))
	
	def onKeyDown(self, event):
		if self.input_vis == True:
			if event.key == 8:
				self.input = self.input[:-1]
			if event.key == 13:
				self.return_callback(self.input)
				self.input_vis, self.input = False, ""
				self.repaint()
			if event.key in range(32, 127):
					self.input += chr(event.key)
