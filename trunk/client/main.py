#!/usr/local/bin/python
#encoding: utf-8
import pygame,math,random,socket,struct,select,sys, types, time
from threading import Thread

class weaponManager():
	def __init__(self):
		pass


class spaceship():
	def __init__(self,pManager, pos=[300,300],id=0, name=''):
		self.speed=[0,0]
		self.acc=[0,0]
		self.rot=0
		self.roting=0
		self.pos=pos
		self.wire=[[-5,-10],[5,-10],[10,10],[-10,10]]
		#self.wire=[[-5,-10], [-10, 10], [10,10]]
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
			pygame.draw.aaline(widok,(255,255,255),(pos[0]+self.wire[i-1][0]*math.cos(self.rot)-self.wire[i-1][1]*math.sin(self.rot),
				  pos[1]+self.wire[i-1][0]*math.sin(self.rot)+self.wire[i-1][1]*math.cos(self.rot)),
				  (pos[0]+self.wire[i][0]*math.cos(self.rot)-self.wire[i][1]*math.sin(self.rot),
				  pos[1]+self.wire[i][0]*math.sin(self.rot)+self.wire[i][1]*math.cos(self.rot)))
			
			rend = self.font.render("[%d] %s (%.1f, %.1f) (%.1f, %.1f)" % (self.id, self.name, self.pos[0], self.pos[1], self.speed[0], self.speed[1]), 0, (255,255,255))
			x= rend.get_rect()
			xx, yy = x[2], x[3]
			
			widok.blit(rend, (pos[0]-(xx/2), pos[1]+self.rect.size[1]))
		self.rect.center=self.pos
 
 # widok.fill((0,255,0),self.rect)
	def update(self):
		#global particles
		self.rot+=self.roting
		self.acc[0]=self.speedchange*math.cos(self.rot+math.pi/2)
		self.acc[1]=self.speedchange*math.sin(self.rot+math.pi/2)
		if self.speedchange:
			self.pManager.addNew(particleEngine([self.pos[0]+self.wire[2][0]*math.cos(self.rot)-self.wire[2][1]*math.sin(self.rot),
				self.pos[1]+self.wire[2][0]*math.sin(self.rot)+self.wire[2][1]*math.cos(self.rot)],(5*self.acc[0]*random.random(),5*self.acc[1]*random.random())))
			self.pManager.addNew(particleEngine([self.pos[0]+self.wire[3][0]*math.cos(self.rot)-self.wire[3][1]*math.sin(self.rot),
				self.pos[1]+self.wire[3][0]*math.sin(self.rot)+self.wire[3][1]*math.cos(self.rot)],(5*self.acc[0]*random.random(),5*self.acc[1]*random.random())))
		self.speed[0]+=self.acc[0]
		self.speed[1]+=self.acc[1]
		self.pos[0]-=self.speed[0]
		self.pos[1]-=self.speed[1]
#particles=[]
 
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
		self.speed = speed
		self.width = 0
		
	def update(self):
		baseParticle.update(self)
		
		self.pos[0]+=self.speed[0]
		self.pos[1]+=self.speed[1]
		if self.ticks < 50:
			self.width = 10-(self.ticks / 5)
			#print(self.width)
		else:
			self.width =0 
		#if self.ticks > 30:
		#	self.width = (self.ticks - 70) / 10
			#self.width = self.width
			
	def draw(self,widok, pos):
		c=120-self.ticks
		if c<0:
			c=0
			print("Wtf")
		color = (c, c, c)
		if self.width <= 1:
			widok.set_at(pos,color)
		else:
			width = self.width/2
			x, y = pos[0] - width, pos[1] - width	  
			widok.fill(color, (x,  y,  self.width, self.width))
 
class particleManager():
	def __init__(self):
		self.particles = []
	def addNew(self, obj):
		self.particles += [obj]
	def updateAll(self):
		for i in self.particles:
			i.update()
			#print("%d %d" % (i.ticks, i.lifetime))
			if i.ticks > i.lifetime:
				self.particles.remove(i)
				
	def count(self):
		return len(self.particles)
	
		
		
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
	def run(self):
		#global particles
		while True:
 
			if self.parent.reading != True:
				for i in self.parent.statki:
					self.parent.statki[i].update()
			self.pingtick += 1
			self.tick += 1
			if self.pingtick > 50:
				#self.ping = [time.time()][0]
				self.parent.parent.client.send(struct.pack('4i', 3, self.parent.statek.id, self.tick, random.randint(0,65535)))
				self.pingtick = 0
			self.parent.particleManager.updateAll()
			self.zegar.tick(50)

				#print("Updated")
class consoleLog():
	def __init__(self):
		self.widok = pygame.Surface((600,200))
		self.widok.set_colorkey((0,0,0))
		self.log = ()
		self.font = pygame.font.Font(None,15)
		self.input_vis = False
		self.input = ""
		self.tick = 0
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
		#self.tick = (self.tick +1) & 20

		v=self.log[-12 if self.input_vis else -13:]
		for i in reversed(range(len(v))):
			#y=200-(i*15)
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
				self.add(self.input)
				self.input_vis, self.input = False, ""
				self.repaint()
			if event.key in range(32, 127):
					self.input += chr(event.key)
		#self.repaint()
			
		

				
				
			
		
"""
class eventThread(Thread):
	def __init__(self, parent):
		Thread.__init__(self)
		self.parent = parent
		self.running = False
		self.start()
		self.ping = 0
		self.time = 0
	def stop(self):
		self.running = False
		self.join()
	def run(self):
		self.running = True
		while self.running:
			self.parent.parent.client.send(struct.pack('4i', 3, self.parent.statek.id, random.randint(0,65535), random.randint(0,65535)))
			#self.parent.console.add("PING")
			self.ping = time.time()
			time.sleep(0.5)
"""			
class gameScreen(baseScreen):
	def __del__(self):
		#self.parent.client.Active = False
		self.parent.client = None
	def __init__(self, surface):
		baseScreen.__init__(self, surface)
		
		self.widok=pygame.Surface((600,600))
		self.panel=pygame.Surface((200,600))
		self.panel.fill((0,0,255))
		for i in range(10):
			pygame.draw.aaline(self.panel,(255,255,255),(i*20,0),(i*20,600))
		self.statek, self.statki = None, {}
		#self.statek=av([100,100],"blabla")
		#self.statki=[self.statek,]
		self.gwiazdy=[]
		for i in range(50):
			self.gwiazdy+=[[random.randint(0,600),random.randint(0,600)],]
			
		self.reading = False
		#[player,]
		
	#self.particles=[] #TODO: Particle manager
		self.pociski=[]
 
		self.keyTable=[]
		self.textfont = pygame.font.Font(None, 25)
		self.particleManager = particleManager()
		self.console = consoleLog()
		self.console.add("Siemano 1")
		self.console.add("Siemano 2")
		#print(self.console.log)
		#self.onKeyDown = self.onKeyDown_proc
		#self.onKeyUp = self.onKeyUp_proc
		self.gameTh = gameThread(self)
		self.gameTh.start()
	def initStatki(self, player):
		self.statki = {player.id: player}
	def drawInfo(self):
		global particles
		self.widok.blit(self.textfont.render("Particles: %d Ping: %d [Chat: %s]" % (self.particleManager.count(), self.gameTh.ping, "True" if self.console.input_vis else "False"),0,(255,255,255)),(0,0))
		#self.widok.blit(self.textfont.render("Particles: %d" % self.particleManager.count(),0,(255,255,255)),(0,0))
 
	def updateScreen(self):
		#global particles
		self.widok.fill((0,0,0))
		for i in self.particleManager.particles:
			i.draw(self.widok,[i.pos[0]-self.statek.pos[0]+300,i.pos[1]-self.statek.pos[1]+300])
 
		if self.statki != {}:
			if self.reading != True:
				for i in self.statki:	  #procedurka przeliczajaca
					self.statki[i].draw(self.widok, [self.statki[i].pos[0]-self.statek.pos[0]+300,self.statki[i].pos[1]-self.statek.pos[1]+300])
					
 
		for i in self.gwiazdy:
			  self.widok.set_at(i,(255,255,255))

		if self.console.input_vis:
			self.console.tick += 1
			if self.console.tick == 41:
				self.console.tick = 0

			self.console.repaint()
		self.widok.blit(self.console.widok, (0, 400))

		self.drawInfo()
		self.parent.wnd.blit(self.widok,(0,0))
		self.parent.wnd.blit(self.panel,(600,0))

	def onKeyDown(self, event):
		#self.keyTable[event.key] = True
		if self.console.input_vis:
			self.console.onKeyDown(event)
			return		

		if event.key == pygame.K_RETURN:
			#self.console.add("ENTER %d" % self.console.count())
			self.console.input_vis = not self.console.input_vis
			if self.console.input_vis:
				self.console.input_vis, self.console.input = True, ""
				
			#self.console.input = "asdasd"
			#self.onKeyDown = self.console.onKeyDown
			#self.onKeyUp = self.console.onKeyUp
	
		if event.key == pygame.K_UP:
			#if self.parent.client == None:
			self.statek.speedchange=0.1
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,2,1))
		if event.key == pygame.K_LEFT:
			#if self.parent.client == None:
			self.statek.roting = -0.1
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,1,-1))
			#self.console.add("onKeyDown(K_LEFT)")
		if event.key == pygame.K_RIGHT:
			#if self.parent.client == None:
			self.statek.roting = 0.1
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,1,1))
	def onKeyUp(self, event):
		if event.key == pygame.K_UP:
			#if self.parent.client == None:
			self.statek.speedchange=0
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,2,0))
		if event.key == pygame.K_LEFT:
			#if self.parent.client == None:
			self.statek.roting = 0
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,1,0))
			#self.console.add("onKeyUp(K_LEFT)")
		if event.key == pygame.K_RIGHT:
			#if self.parent.client == None:
			self.statek.roting = 0
			self.parent.client.send(struct.pack('iiii', 11,self.statek.id,1,0))
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
			print("%s %s" % (self.login, self.password))
 
			#self.parent.connection = socketThread((self.login, self.password))
			self.parent.client.Active = True
			#self.client.connect()
 
		if event.key == pygame.K_ESCAPE:
			self.parent.activeScreen=mainScreen(self.parent)
		if event.key in range(ord('A'), ord('Z')+1) or event.key in range(ord('a'), ord('z')+1):
			if self.fieldIndex == 0:
				self.login += chr(event.key)
			elif self.fieldIndex == 1:
				self.password += chr(event.key)
		   
		if event.key == pygame.K_TAB:
			#self.fieldIndex = 1 if self.fieldIndex == 0 else 0
			#self.tick, self.b = 127, True
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
			#self.menuIndex=(self.menuIndex - 1) if self.menuIndex-1 >= 0 else len(self.menu)-1
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
		self.client = clientSocket({
			'host': '5.152.103.178',
			#'host': 'python.org',
			#'port': int(sys.argv[1]),
			'port' : 12345,
			#'onConnecting': self.onConnecting,
			'onConnect': self.onConnect,
			'onDisconnect': self.onDisconnect,
			'onError': self.onError,
			'onRead': self.onRead,
			'onFinish': self.onFinish})
	def onFinish(self, sender):
		#self.client = None if self.client != None else None
		print "Finish"
		
	def onConnect(self, sender):
		print "Connected to %s:%d" % sender.connection
		#print(isinstance(self.activeScreen,loginScreen))
		if isinstance(self.activeScreen, loginScreen):
			#print("From main : %s %s" % (self.activeScreen.login, self.activeScreen.password))
			sender.send(struct.pack("iiii",0, 1, len(self.activeScreen.login),len(self.activeScreen.password)))
			sender.send(self.activeScreen.login + self.activeScreen.password)
		#sender.sock.send(struct.pack("ss", self.login, self.password))
		#sender.sock.send("GET / HTTP/1.0\r\n\r\n")
			
		
	def onDisconnect(self, sender):
		print "Disconnected to %s:%d" % sender.connection
		self.activeScreen=mainScreen(self)
		
	def onError(self, sender, error):
		print "Error: %s" % error
		self.activeScreen=mainScreen(self)
	def onRead3(self, sender, data):
		if len(data)<4:
			return
		if len(data) == 4:
			p_id = struct.unpack('i', data)
			if p_id == 0:
				rcv = sender.recv_proc(12)
				rcv = struct.unpack('iii', rcv)
				print(rcv)
			
		
	def onRead(self, sender, data):
		while len(data)>0:
			if len(data[0:16]) < 4:
				continue
			rcv=struct.unpack('iiii',data[0:16])
			
			#print(rcv)
			dl = 16
			if rcv[0] == 0:
				if rcv == (0,0,0,0):
					self.activeScreen=mainScreen(self)
				else:
					print "Zalogowalem sie!"
					#print(rcv)
					self.activeScreen=gameScreen(self)
					self.activeScreen.statek = spaceship(self.activeScreen.particleManager, [rcv[2], rcv[3]], rcv[1])
					#self.activeScreen.eventTh = eventThread(self.activeScreen)
	
					self.activeScreen.initStatki(self.activeScreen.statek)
					print(self.activeScreen.statki)
					
					#self.activeScreen.statek.
				dl = 16
			if rcv[0] == 2: #statek nowy obieku
				data2 = data[12:]
				ship_id = rcv[1]
				nick_len = struct.unpack('i', data2[4*8:(4*8)+4])[0]
				nick = data2[(4*8)+4:(4*8)+4+nick_len]
				statek = (nick,) + struct.unpack('8f',data2[:4*8])
				
				if ship_id == self.activeScreen.statek.id:
					self.activeScreen.statek.name = statek[0]
				else:
					self.activeScreen.reading = True
					self.activeScreen.statki[ship_id]=spaceship(self.activeScreen.particleManager, [statek[1], statek[2]], ship_id, statek[0])
					self.activeScreen.reading = False

				dl = 12+(4*8)+4+nick_len
			if rcv[0] == 3:
				ship_id = rcv[1]
				#self.activeScreen.gameTh.time = time.time() - self.activeScreen.gameTh.ping
				ping = rcv[2]
				self.activeScreen.gameTh.ping = self.activeScreen.gameTh.tick - rcv[2]
				#ping = ping / 2
				
				print self.activeScreen.gameTh.time
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
			if rcv[0] == 7: 
				#print("Quit:")
				#print(rcv)
				#print("")
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
				if ship.speed[1] != 0:
					print (rcv[3] - ship.pos[1]) / ship.speed[1]
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
					print "New speed: %f %f" % (rcv[2], rcv[3])
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
			data=data[dl:]
			
 
	
class Game(connectionClass):
	def __init__(self, width, height):
		connectionClass.__init__(self)
		self.wnd = pygame.display.set_mode((width, height))
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
		print("UDP SEND : %s"% data)
		print(self.connection)
		self.sock.sendto(data, self.connection)
	def tcp_recv(self, count):
		return self.sock.recv(count)
	def udp_recv(self, count):
		#return self.sock.recvfrom(count)
		
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
			#self.sock.sendto(data)
			self.send_proc(data)
		except socket.error, e:
			self.data['onError'](self, e) if self.data['onError'] != None else None
			
	def connect_to(self, where=()): 
		if self.UDP == False:
			try:
				#if where != ():
				#	self.connection = where
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
			#data = self.sock.recv(8192)
			a, b, c = select.select([self.sock], [], [])
			for s in a:
				#data = self.recv_proc(1024)
				data,y = s.recvfrom(1024)
				#print("REC LEN: %d" % len(data))
				if not data:
					self.onDisconnect()
					break
				self.data['onRead'](self, data) if self.data['onRead'] != None else None
	def connect(self,where=()):
		if where!=():
			self.connection=where
		#self.connect_to(self)
		#self.connect()
		#self.sock.close()
		#self.sock = None
		self.start()
	   
	def run(self):
		#self.start()
		self.connect_to()
		self.data['onFinish'](self) if self.data['onFinish'] != None else None
	def onDisconnect(self):
		self.fActive=False
		self.sock.close()
		self.data['onDisconnect'](self) if self.data['onDisconnect'] != None else None
	def disconnect(self):
		#self.fActive=False
		#self.sock.close()
		self.onDisconnect()
		#print("Disconnect")
 
	def getActive(self):
		return self.fActive
	def setActive(self, value):
		self.fActive = value
		self.start() if self.fActive else self.disconnect()
	
	Active = property(getActive, setActive)
 
game = Game(800, 600)
game.runGame(mainScreen(game))
 
 
"""def onConnect(sender):
   print("Connected to %s:%d" % sender.connection)
   sender.sock.send("GET / HTTP/1.0\r\n\r\n")
   
def onDisconnected(sender):
   print("Disconnected to %s:%d" % sender.connection)
   
def onRead(sender, data):
   print("GET %d bytes" % (len(data)))
   #sender.Active=False
def onConnecting(sender):
   print("Connecting to %s:%d" % sender.connection)
def onError(sender, error):
   print("Error: %s" % error)
   
def onFinish(sender):
   print("Finished")
 
x=clientSocket({'host': "python.org",
			   'port': 80,
			   'onConnecting': onConnecting,
			   'onConnect': onConnect,
			   'onDisconnect': onDisconnected,
			   'onRead': onRead,
			   'onError': onError,
			   'onFinish': onFinish})
x.Active=True"""
