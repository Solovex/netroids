#!/usr/local/bin/python
#encoding: utf-8
import pygame,math,random,socket,struct,select,sys, types, time,pygame.surfarray
from threading import Thread

from spaceship import spaceship
from particles import *
from weapons import *
from client_socket import *
from screen import *
	
class connectionClass():
	def __init__(self):
		self.create(False)
	def create(self, doDelete):
		if doDelete:
			del self.client
		self.client = clientSocket({
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
		
	def onDisconnect(self, sender):
		print "Disconnected to %s:%d" % sender.connection
		self.activeScreen=mainScreen(self)
		
	def onError(self, sender, error):
		print "Error: %s" % error
		self.activeScreen=mainScreen(self)
		
	def onRead(self, sender, data):
		while len(data)>0:
			if len(data[0:4]) < 4:
				print "Bad size: %d = %s" % (len(data), repr(data))
				continue
			rcv=struct.unpack('i', data[0:4])
			if len(data) == 12:
				rcv+=struct.unpack('2i', data[4:12])
			elif len(data) == 16:
				rcv+=struct.unpack('3i', data[4:16])
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
					self.activeScreen.statki[ship_id].speed, self.activeScreen.statki[ship_id].acc, self.activeScreen.statki[ship_id].rot, self.activeScreen.statki[ship_id].roting = [statek[4], statek[5]], [statek[6], statek[7]], statek[8], statek[9]
					print statek[0] , " chuj speed: " , self.activeScreen.statki[ship_id].speed
					print 'NOWY STATEK! Name: ',statek[0],' MODEL ',rcv[2]

					self.activeScreen.reading = False
				dl = 12+(4*8)+4+len(nick)
			if rcv[0] == 3:
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
				rcv=struct.unpack('2i2f', data[0:16])
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
				rcv=struct.unpack('2i2f', data[0:16])
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
				rcv=struct.unpack('2i2f', data[0:16])
				ship_id = rcv[1]
				ship = self.activeScreen.statki.get(ship_id, None)
				if ship != None:
					ship.acc=[rcv[2], rcv[3]]
				else:
					print("Unknown statek ID:%d" % ship_id)
 
				dl = 16
			if rcv[0] == 11: #obrot z serwera
				rcv=struct.unpack('3if',data[0:16])
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
		self.zegar=pygame.time.Clock()
		pygame.display.set_caption("netroids")
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

def main():
	game = Game(800, 600)
	game.runGame(mainScreen(game))

if __name__ == '__main__': main()
