#!/usr/local/bin/python
#encoding: utf-8
import pygame,math,random,socket,struct,select,sys, types, time,pygame.surfarray
from threading import Thread

class spaceship():
	def __init__(self,pManager, pos=[300,300],id=0, name='',model=0):
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
 
class baseParticle():
	def __init__(self, pos, lifetime):
		self.pos, self.lifetime = pos, lifetime
		self.ticks = 0
	def update(self):
		self.ticks += 1
		pass
	def draw(self, widok, pos):
		pass
 
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
		baseParticle.__init__(self, pos, 80)
		max_speed = 2
		self.speed = speed[:]
		for i in range(2):
			if self.speed[i] < ~max_speed+1:
				self.speed[i] = ~max_speed+1
			elif self.speed[i] > max_speed:
				self.speed[i] = max_speed
			elif self.speed[i] > 0 and self.speed[i]<1:
				self.speed[i] = 1
			elif self.speed[i] > -1 and self.speed[i]<0:
				self.speed[i] = -1
			self.speed[i]=self.speed[i]+ (self.speed[i] * random.random())

		
	def update(self):
		baseParticle.update(self)
		self.pos[0]+=self.speed[0]
		self.pos[1]+=self.speed[1]
	def draw(self, widok, pos):
		x=[(self.lifetime*1.5)-self.ticks] * 3
		widok.fill(x, (pos[0], pos[1], 1, 1)) #zamiast set_at

class particleManager():
	def __init__(self):
		self.particles = []
	def addNew(self, obj):
		self.particles += [obj]
	def updateAll(self):
		for i in self.particles:
			i.update()
			if i.ticks > i.lifetime:
				self.particles.remove(i)
				
	def count(self):
		return len(self.particles)

class baseWeapon(baseParticle):
	def __init__(self, start, rot, distance_max, pMgr, effect):
		baseParticle.__init__(self, start, 255)
		self.start = start[:]
		self.rot = rot
		self.distance_max = distance_max
		self.effect = effect #klasa okreslajaca efekty broni podczas updatowania (najczesciej latania)
		self.pMgr = pMgr
	def distance(self):
		return ( ((self.pos[0]-self.start[0]) ** 2) + ((self.pos[1]-self.start[1]) ** 2) )

class rocketWeapon(baseWeapon):
	def __init__(self, pMgr, start, rot):
		baseWeapon.__init__(self, start, rot, 1000000, pMgr, particleRocket)
		self.width, self.height = 2, 10
		self.wire = [[-self.width, -self.height] , [self.width, -self.height], [self.width, self.height], [-self.width, self.height]] #pocisk

		self.vect = 1
		self.speed_up = 15 #wzrost predkosci
		self.setSpeed()
		

	def setSpeed(self):
		self.speed = map(lambda x: -x, [self.vect*math.cos(self.rot+math.pi/2), self.vect*math.sin(self.rot+math.pi/2)])

	def update(self):
		baseWeapon.update(self)
		spaliny = 26
		if self.ticks >= self.speed_up:
			self.vect = (self.ticks/10) ** 2
			self.setSpeed()
			spaliny = 4
		map(lambda p: self.pos.__setitem__(p, self.pos.__getitem__(p) + self.speed.__getitem__(p)), range(2))
		
		for i in range(random.randint(int(spaliny/2), spaliny)):
			self.pMgr.addNew(self.effect(map(lambda x: x+random.randint(-2,2), self.pos[:]), map(lambda x: -x, self.speed[:])))

	def draw(self, widok, pos):
		pts = []
		for i in range(len(self.wire)):
			pts.append([ pos[0] + self.wire[i][0] * math.cos(self.rot) - self.wire[i][1] * math.sin(self.rot), pos[1] + self.wire[i][0] * math.sin(self.rot) + self.wire[i][1] * math.cos(self.rot)])
		pygame.draw.polygon(widok, (255, 255, 255), pts)
	
class weaponManager():
	def __init__(self, screen):
		self.parent = screen
		self.bullets = []

	def shoot(self, ship_id, class_name):
		self.bullets.append(class_name(self.parent.particleManager, self.parent.statki[ship_id].pos[:], self.parent.statki[ship_id].rot))

	def count(self):
		return len(self.bullets)

	def updateAll(self):
		for i in self.bullets:
			i.update()
			d = i.distance()
			if d > i.distance_max:
				self.bullets.remove(i)
	
class baseScreen(): #bazowa klasa
	def __init__(self, surface):
		self.parent = surface
		self.surface = self.parent.wnd
		
	def updateScreen(self):
		pass
					
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
				i.draw(self.widok, [x,y])
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
			#bad self.weaponManager.shoot(self.statek.id, rocketWeapon)
			
			self.parent.client.send(struct.pack('4i',13,0,0,0))
		if event.key == pygame.K_BACKSPACE:
			self.parent.client.send(struct.pack('2i',14, 2))
		if event.key == pygame.K_UP:
			#self.statek.speedchange=0.1
			self.parent.client.send(struct.pack('iii', 11,2,1))
		if event.key == pygame.K_DOWN:
			#self.statek.speedchange=-0.1
			self.parent.client.send(struct.pack('iii', 11,2,-1))			
		if event.key == pygame.K_LEFT:
			#self.statek.roting = -0.1
			self.parent.client.send(struct.pack('iii', 11,1,-1))
		if event.key == pygame.K_RIGHT:
			#self.statek.roting = 0.1
			self.parent.client.send(struct.pack('iii', 11,1,1))
	def onKeyUp(self, event):
		if event.key == pygame.K_UP:
			#self.statek.speedchange=0
			self.parent.client.send(struct.pack('iii', 11,2,0))
		if event.key == pygame.K_DOWN:
			#self.statek.speedchange=0
			self.parent.client.send(struct.pack('iii', 11,2,0))			
		if event.key == pygame.K_LEFT:
			#self.statek.roting = 0
			self.parent.client.send(struct.pack('iii', 11,1,0))
		if event.key == pygame.K_RIGHT:
			#self.statek.roting = 0
			self.parent.client.send(struct.pack('iii', 11,1,0))
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

############################################################################################################################	

class connectionClass():
	def __init__(self):
		self.create(False)
	def create(self, doDelete):
		if doDelete:
			del self.client
		self.client = clientSocket({
			#'host': '5.152.103.178',
			'host' : sys.argv[1],
			'port' : 12345,
			'onConnect': self.onConnect,
			'onDisconnect': self.onDisconnect,
			'onError': self.onError,
			'onRead': self.onRead,
			'onFinish': self.onFinish})
	def reinit(self):
		self.create(True)
	def onFinish(self, sender):
		print "Finish"
		
	def onConnect(self, sender):
		print "Connected to %s:%d" % sender.connection
		if isinstance(self.activeScreen, loginScreen):
			sender.send(struct.pack("3i",0,len(self.activeScreen.login),len(self.activeScreen.password)) + self.activeScreen.login + self.activeScreen.password)
			#sender.send(self.activeScreen.login + self.activeScreen.password)
		
	def onDisconnect(self, sender):
		print "Disconnected to %s:%d" % sender.connection
		self.activeScreen=mainScreen(self)
		
	def onError(self, sender, error):
		print "Error: %s" % error
		self.activeScreen=mainScreen(self)
		
	def onRead(self, sender, data):
		while len(data)>0:
			#if len(data[0:12]) < 12:
				#p_id = -1
				#if len(data[0:4]) == 4:
				#	p_id = struct.unpack('i', data[0:4])[0]
				#print "Bad size: %d = %s PACKET ID = %d" % (len(data), data, p_id)
				#continue
			if len(data[0:4]) < 4:
				print "Bad size: %d = %s" % (len(data), repr(data))
				continue
			#rcv=struct.unpack('iii',data[0:12]) if len(data) == 12 else struct.unpack('iii')
			rcv=struct.unpack('i', data[0:4])
			if len(data) == 12:
				rcv+=struct.unpack('2i', data[4:12])
			elif len(data) == 16:
				rcv+=struct.unpack('3i', data[4:16])
			#print("UNPACK LEN: %d/ %d/ %d" % (rcv[0], len(data), len(rcv)))
			#print(rcv)
			dl = len(data)
			if rcv[0] == 0:
				if rcv == (0,0,0,0):
					self.activeScreen=mainScreen(self)
				else:
					print "Zalogowalem sie!"
					self.activeScreen=gameScreen(self)
					self.activeScreen.statek = spaceship(self.activeScreen.particleManager, [rcv[2], rcv[3]], rcv[1])
	
					self.activeScreen.initStatki(self.activeScreen.statek)
				
				dl = 16
			if rcv[0] == 2: #statek nowy obieku
				rcv = struct.unpack('3i8fi', data[0:12*4])
				nick = data[12*4:12*4+rcv[-1]]
				statek = (nick, ) + rcv[2:]
				ship_id = rcv[1]
				if ship_id == self.activeScreen.statek.id:
					self.activeScreen.statek.name = statek[0]
				else:
					self.activeScreen.reading = True
					self.activeScreen.statki[ship_id]=spaceship(self.activeScreen.particleManager, [statek[2], statek[3]], ship_id, statek[0],rcv[2])
					print 'NOWY STATEK! Name: ',statek[0],' MODEL ',rcv[2]
					self.activeScreen.reading = False
				dl = 12+(4*8)+4+len(nick)
			if rcv[0] == 3:
				#ship_id = rcv[1]
				ping = rcv[1]
				self.activeScreen.gameTh.ping = self.activeScreen.gameTh.tick - rcv[1]
				dl = 12
				

			if rcv[0] == 7: 
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					self.activeScreen.reading=True
					self.activeScreen.statki.pop(ship_id)
					self.activeScreen.reading=False
				else:
					print("Uknown statek ID:%d" % ship_id)
				dl = 16
			if rcv[0] == 8:
				rcv=struct.unpack('iiff', data[0:16])
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					ship.pos=[rcv[2], rcv[3]]
					ship.pos[0]+=self.activeScreen.gameTh.ping*ship.speed[0]
					ship.pos[1]+=self.activeScreen.gameTh.ping*ship.speed[1]
				else:
					print("Unknown statek ID:%d" % ship_id)
 
				dl = 16
			if rcv[0] == 9:
				rcv=struct.unpack('iiff', data[0:16])
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					ship.speed=[rcv[2], rcv[3]]
					ship.speed[0]+=self.activeScreen.gameTh.ping * ship.acc[0]
					ship.speed[1]+=self.activeScreen.gameTh.ping * ship.acc[1]
				else:
					print("Unknown statek ID:%d" % ship_id)
 
				dl = 16

			if rcv[0] == 10:
				rcv=struct.unpack('iiff', data[0:16])
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					ship.acc=[rcv[2], rcv[3]]
				else:
					print("Unknown statek ID:%d" % ship_id)
 
				dl = 16
			if rcv[0] == 11: #obrot z serwera
				rcv=struct.unpack('iiif',data[0:16])
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					if rcv[2] == 0:
						ship.rot = rcv[3]
					elif rcv[2] == 1:
						ship.roting = rcv[3]
					elif rcv[2] == 2:
						ship.speedchange = rcv[3]
				else:
					print("Unknown statek ID:%d" % ship_id)
			if rcv[0] == 12:
				if rcv[1] == self.activeScreen.statek.id:
					txt = data[16:16+rcv[2]]
					self.activeScreen.console.add(txt)
				else:
					print("Blad chatu")
				dl=16+rcv[2]
			if rcv[0] == 13:
				print 'strzela z rotem', rcv[2]
#				self.activeScreen.statki.get(rcv[1], None).rot=rcv[2]
				self.activeScreen.weaponManager.shoot(rcv[1], rocketWeapon)
				dl = 16
			if rcv[0] == 14:
				rcv=struct.unpack('2i', data[0:8])
				if rcv == (14, 0):
					self.activeScreen.console.add(u'Wiem że się zadokowałem')
				else:
					self.activeScreen.console.add(u'Coś spierdolone!')				
				dl = 8

			data=data[dl:]
			
class Game(connectionClass):
	def __init__(self, width, height):
		connectionClass.__init__(self)
		self.wnd = pygame.display.set_mode((width, height))
		pygame.display.set_caption("netroids")
		self.zegar=pygame.time.Clock()
		self.activeScreen=None
		pygame.init()
	
	def runGame(self, startScreen):
		self.activeScreen=startScreen
		self.mainLoop()
 
	def mainLoop(self):
		while True:
			self.activeScreen.updateScreen()
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit(0)
					break
				else:
					evN="on"+pygame.event.event_name(event.type) #:D
					if evN in dir(self.activeScreen):
						getattr(self.activeScreen, evN)(event) #

class clientSocket(Thread):
	def __init__(self, data):
		if not ('host' in data and 'port' in data):
			raise ValueError
		Thread.__init__(self)
		self.fActive=False
		self.data = data
		self.UDP = True
		
		#self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if self.UDP == True else socket.SOCK_STREAM)
		if self.UDP == True:
			self.send_proc = self.udp_send
			self.recv_proc = self.udp_recv
		else:
			self.send_proc = self.tcp_send
			self.recv_proc = self.tcp_recv
			
		self.connection=(self.data['host'], self.data['port'])
		events = ['onConnect','onConnecting','onDisconnect', 'onRead', 'onError','onFinish']
		for event in events:
			if event not in self.data:
				self.data[event]=None
	def tcp_send(self, data):
		self.sock.send(self, data)
		print("TCP SEND : %s"% data)

	def udp_send(self, data):
		self.sock.sendto(data, self.connection)

	def tcp_recv(self, count):
		return self.sock.recv(count)

	def udp_recv(self, count):
		asdf = self.sock.recvfrom(count)
		print asdf
		return asdf[0]

	def __del__(self):
		self.sock.close()
		print("Socket destructor!")
		
	def send(self, data):
		if self.fActive == False:
			return
		try:
			self.send_proc(data)
		except socket.error, e:
			self.data['onError'](self, e) if self.data['onError'] != None else None
			
	def connect_to(self, where=()): 
		if self.UDP == False:
			try:
				self.data['onConnecting'](self) if self.data['onConnecting'] != None else None
				self.sock.connect(self.connection)
			except socket.gaierror, e:
				self.data['onError'](self, e) if self.data['onError'] != None else None
				#sys.exit(1)
				return False
			except socket.error, e:
				self.data['onError'](self, e) if self.data['onError'] != None else None
				return False
		
		self.data['onConnect'](self) if self.data['onConnect'] != None else None
		while self.fActive:
			a, b, c = select.select([self.sock], [], [])
			for s in a:
				data, y = s.recvfrom(1024)

				if not data:
					self.onDisconnect()
					break
				self.data['onRead'](self, data) if self.data['onRead'] != None else None

	def connect(self,where=()):
		if where!=():
			self.connection=where
		self.start()
	   
	def run(self):
		self.connect_to()
		self.data['onFinish'](self) if self.data['onFinish'] != None else None

	def onDisconnect(self):
		self.fActive=False
		self.sock.close()
		self.data['onDisconnect'](self) if self.data['onDisconnect'] != None else None

	def disconnect(self):
		self.onDisconnect()

	def getActive(self):
		return self.fActive

	def setActive(self, value):
		self.fActive = value
		self.start() if self.fActive else self.disconnect()
	
	Active = property(getActive, setActive)

game = Game(800, 600)
game.runGame(mainScreen(game))
