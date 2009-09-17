#encoding: utf-8
import pygame, random
from base_class import *
from managers import *
from console import *
from threads import *
from client_socket import *
from spaceship import *
from particles import *
from weapons import *
class gameScreen(baseScreen):
	def __del__(self):
		self.parent.client = None
	def __init__(self, surface):
		baseScreen.__init__(self, surface)
		
		self.widok=pygame.Surface((600,600))
		self.panel=pygame.Surface((200,600))
		self.panel.fill((0,0,255))
		for i in range(10):
			pygame.draw.aaline(self.panel,(255,255,255),(i*20,0),(i*20,600))
		self.statek, self.statki = None, {}
		self.gwiazdy=[]
		for i in range(50):
			self.gwiazdy+=[[random.randint(0,600),random.randint(0,600)],]
			
		self.reading = False
		
		self.keyTable=[]
		self.textfont = pygame.font.Font(None, 25)
		self.particleManager = particleManager()
		self.weaponManager = weaponManager(self)
		self.console = consoleLog(self.onConsoleReturn)
		self.gameTh = gameThread(self)
		self.gameTh.start()

	def initStatki(self, player):
		self.statki = {player.id: player}

	def drawInfo(self):
		self.widok.blit(self.textfont.render("Particles: %d Bullets: %d Ping: %d" % (self.particleManager.count(), self.weaponManager.count(), self.gameTh.ping), 0, (255,255,255)) , (0,0))
 
	def updateScreen(self):

		self.widok.lock()
		self.widok.fill((0,0,0))
		for i in self.particleManager.particles + self.weaponManager.bullets:
			x, y = i.pos[0]-self.statek.pos[0]+300, i.pos[1]-self.statek.pos[1]+300
			if (x>0 and x<600) and (y>0 and y<600): #rysuj particle tylko jak sa widoczne
				i.draw(self.widok, (x,y))
		self.widok.unlock()


		if self.reading != True:
				for i in self.statki.keys():	  #procedurka przeliczajaca
					self.statki[i].draw(self.widok, [self.statki[i].pos[0]-self.statek.pos[0]+300,self.statki[i].pos[1]-self.statek.pos[1]+300])


					
 
		for i in self.gwiazdy:
			  self.widok.set_at(i,(255,255,255))

		if self.console.input_vis:
			self.console.tick += 1
			if self.console.tick == 41:
				self.console.tick = 0

			self.console.repaint()
		
		#self.widok.unlock()
		self.drawInfo()

		#self.parent.wnd.lock()
		self.parent.wnd.blit(self.widok,(0,0))
		self.parent.wnd.blit(self.panel,(600,0))
		self.parent.wnd.blit(self.console.widok, (0, 400))
		#self.parent.wnd.unlock()
	def onConsoleReturn(self, text):
		print "no to wyslalem chat o dlugosci %d"%len(text)
		self.parent.client.send(struct.pack('4i', 12, self.statek.id, len(text), 0) + text)
	
	def onKeyDown(self, event):
		if self.console.input_vis:
			self.console.onKeyDown(event)
			return		

		if event.key == pygame.K_RETURN:
			self.console.input_vis = not self.console.input_vis
			if self.console.input_vis:

				self.console.input_vis, self.console.input = True, ""
		if event.key == pygame.K_SPACE:
			print("wcisnalem spacje rot: %d" % self.statek.rot)
			if self.parent.client == None or self.parent.client.Active == False:
				self.weaponManager.shoot(self.statek.id, rocketWeapon)
			self.parent.client.send(struct.pack('4i',13,0,0,0))
		if event.key == pygame.K_BACKSPACE:
			self.parent.client.send(struct.pack('2i',14, 2))
		if event.key == pygame.K_UP:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.speedchange=0.1
			self.parent.client.send(struct.pack('3i', 11,2,1))
		if event.key == pygame.K_DOWN:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.speedchange=-0.1
			self.parent.client.send(struct.pack('3i', 11,2,-1))			
		if event.key == pygame.K_LEFT:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.roting = -0.1
			self.parent.client.send(struct.pack('3i', 11,1,-1))
		if event.key == pygame.K_RIGHT:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.roting = 0.1
			self.parent.client.send(struct.pack('3i', 11,1,1))
	def onKeyUp(self, event):
		if event.key == pygame.K_UP:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.speedchange=0
			self.parent.client.send(struct.pack('3i', 11,2,0))
		if event.key == pygame.K_DOWN:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.speedchange=0
			self.parent.client.send(struct.pack('3i', 11,2,0))			
		if event.key == pygame.K_LEFT:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.roting = 0
			self.parent.client.send(struct.pack('3i', 11,1,0))
		if event.key == pygame.K_RIGHT:
			if self.parent.client == None or self.parent.client.Active == False: self.statek.roting = 0
			self.parent.client.send(struct.pack('3i', 11,1,0))

class loginScreen(baseScreen):
	def __init__(self, surface):
		baseScreen.__init__(self, surface)
		self.textfont = pygame.font.Font(None, 25)
		self.tick = 127
		self.b = True
		self.login = self.password = ""
		self.fields=[pygame.Rect(100,100,300,20),pygame.Rect(100,200,300,20)]
		self.fieldIndex=0
 
	def updateScreen(self):
		self.tick = (self.tick+1 if self.b == True else self.tick-1) & 255
		if self.tick == 255:
			self.b = False
		if self.tick == 127:
			self.b = True
		self.surface.fill((0,0,0))
		txtLogin=self.textfont.render(self.login,0,(255,0,0))
		txtPwd=self.textfont.render(self.password,0,(255,0,0))
		[pygame.draw.rect(self.surface,(0,self.tick,0) if i == self.fieldIndex else (0,255,0),self.fields[i]) for i in range(0, len(self.fields))]
		self.surface.blit(self.textfont.render(u"Login:",0,(255,0,0)),(100,75))
		self.surface.blit(self.textfont.render(u"Hasło:",0,(255,0,0)),(100,175))
		self.surface.blit(txtLogin,(100,100))
		self.surface.blit(txtPwd,(100,200))
 
	def activateField(self, fldIndex):
		self.fieldIndex = fldIndex
		self.tick, self.b = 127, True
 
		
	def onMouseButtonUp(self, event):
		for i in range(0,len(self.fields)):
			if self.fields[i].collidepoint(event.pos):
				self.activateField(i)
 
	def onKeyDown(self, event):
		if event.key == pygame.K_BACKSPACE:
			if self.fieldIndex == 0:
				self.login = self.login[0:len(self.login)-1]
			elif self.fieldIndex == 1:
				self.password = self.password[0:len(self.password)-1]
 
	def onKeyUp(self, event):
		if event.key == 13:
			self.parent.reinit()
			self.parent.client.Active = True
 
		if event.key == pygame.K_ESCAPE:
			self.parent.activeScreen=mainScreen(self.parent)
		if event.key in range(ord('A'), ord('Z')+1) or event.key in range(ord('a'), ord('z')+1):
			if self.fieldIndex == 0:
				self.login += chr(event.key)
			elif self.fieldIndex == 1:
				self.password += chr(event.key)
		   
		if event.key == pygame.K_TAB:
			self.activateField(1 if self.fieldIndex == 0 else 0)
														
		
class mainScreen(baseScreen): #menu
	def __init__(self, surface):
		baseScreen.__init__(self, surface)
		self.font = pygame.font.Font(None, 55)
		self.menu = ['Login', 'Opcje',  'Pomoc', 'Exit']
		self.menuIndex = 0
	
	def updateScreen(self):
		self.surface.fill((0,0,0))
		for menuItem in range(0,len(self.menu)):
			self.surface.blit(self.font.render(self.menu[menuItem], 0, (255, 0, 0) if menuItem == self.menuIndex else (255,255,255)), (100, 75+(menuItem*55)))
	
	def onKeyUp(self, event):
 
		if event.key == pygame.K_UP:
			self.menuIndex=(self.menuIndex -1) & (len(self.menu)-1)
		elif event.key == pygame.K_DOWN:
			self.menuIndex=(self.menuIndex +1) & (len(self.menu)-1)
		elif event.key == pygame.K_RETURN:
			print("Menu : %s" % (self.menu[self.menuIndex]))
			
			if self.menuIndex == 3:
				pygame.event.post(pygame.event.Event(pygame.QUIT,{}))
			elif self.menuIndex == 0:
				self.parent.activeScreen = loginScreen(self.parent)
			elif self.menuIndex == 1:
				self.parent.activeScreen = gameScreen(self.parent)
				self.parent.activeScreen.statek = spaceship(self.parent.activeScreen.particleManager, [100,100], 0, "Drajwer")
				self.parent.activeScreen.statki={0: self.parent.activeScreen.statek}
