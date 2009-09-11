#!/usr/local/bin/python
import socket,threading,pygame,select,os,sys,struct,math,time


def dictIndex(whereToLook,whatToFind):
 for i in whereToLook.items():
  if i[1]==whatToFind:
   return i[0]

class server:
 def __init__(self):
  self.server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
  self.server.bind(("",int(sys.argv[1])))
#  self.server.listen(5)

  self.sockety={0:sys.stdin,1:self.server}
  self.accounts={'asdf':'asdf',
  		 'qwer':'qwer',
		 'zxcv':'zxcv'
		}
  self.db={'asdf':{'socket':None,'pos':[100,100]},
  	   'qwer':{'socket':None,'pos':[150,100]},
	   'zxcv':{'socket':None,'pos':[1500,1500]}
	  }
  self.running=1
  self.statki={}
 def run(self):
  while self.running:
   self.input,self.output,self.exc=select.select([sys.stdin,self.server],[],[],0.1) 
   for s in self.input:
    if s==self.server:
     self.data,self.adres=self.server.recvfrom(1024)
     if self.sockety.values().count(self.adres)==0:
      self.handleConnection(self.adres)
      print 'dodalem ',self.adres,' do listy! lista: ',self.sockety
     print 'data', struct.unpack('4i',self.data)
     self.typ,self.id,self.arg1,self.arg2=struct.unpack('4i',self.data)
     if self.typ==0:
        print 'odbieram wielkosc: ',struct.calcsize("%ss%ss"%(self.arg1,self.arg2))
        self.loginData,self.adres=self.server.recvfrom(1024)
	print 'logindata: ',self.loginData,self.adres
        if self.loginData=='':
         self.handleQuit(self.adres)
        self.login,self.pwd=struct.unpack("%ss%ss"%(self.arg1,self.arg2),self.loginData)
	print self.login,self.pwd
        self.handleLogin(self.adres,self.login,self.pwd)
       
     if self.typ==11:
        if self.id==dictIndex(self.sockety,self.adres):
         self.changeVar(self.id,self.arg1,self.arg2)
	else:
	 self.server.sendto(struct.pack('4i',0,0,0,0),self.adres)
	 
     if	self.typ==3: 
      print self.id,' mial ping ',self.statki[self.id][8]
      self.statki[self.id][8]=0
      self.server.sendto(struct.pack('4i',3,self.id,self.arg1,self.arg2),self.adres)
      
    if s==sys.stdin:
	pass

 def handleConnection(self,target):
  self.sockety[max(self.sockety.keys())+1]=target
  print 'Nowe polaczenie: ',target
 
 def handleLogin(self,sock,login,pwd):
  print 'bedzie login'
  if self.accounts.has_key(login):
   if self.accounts[login]==pwd and self.db[login]['socket']==None:
    self.db[login]['socket']=dictIndex(self.sockety,sock)
    self.statki[dictIndex(self.sockety,sock)]=[login,[self.db[login]['pos'][0],self.db[login]['pos'][1]],[],[0,0],[0,0],0,0,0,0]
    self.server.sendto(struct.pack('4i',0,dictIndex(self.sockety,sock),self.db[login]['pos'][0],self.db[login]['pos'][1]),sock)
    self.updateAllSets()
    print login,' sie zalogowal'
   else:
    self.server.sendto(struct.pack('4i',0,0,0,0),sock)
  else:
   self.server.sendto(struct.pack('4i',0,0,0,0),sock)

   

 def handleQuit(self,sock):
  print "kogos wyjebalo"
  try:
   self.db[self.statki[dictIndex(self.sockety,sock)][0]]['socket']=None
   self.statki.pop(dictIndex(self.sockety,sock))
   print self.statki
  except:
   print 'wyjebalo kogos kto sie nie zalogowal' 
  self.sockety.pop(dictIndex(self.sockety,sock))
  self.updateAllSets()
  self.server.sendto(struct.pack('4i',666,666,666,666),sock)
   
  
 def updateRelevantSet(self,target):
  for i in self.statki.keys():
   if self.statki[target][2].count(i)==0 and (self.statki[target][1][0]-self.statki[i][1][0])**2+(self.statki[target][1][1]-self.statki[i][1][1])**2<360000:
    print self.statki[target][0],' ma w relevant secie ',self.statki[i][0]
    self.statki[target][2].append(i)
    self.sendNewObject(target,i)
   if self.statki[target][2].count(i)==1 and (self.statki[target][1][0]-self.statki[i][1][0])**2+(self.statki[target][1][1]-self.statki[i][1][1])**2>1000000:
    print self.statki[target][0],' juz nie ma w relevant secie ',self.statki[i][0]
    self.statki[target][2].remove(i)
  for i in self.statki[target][2]:
   if not self.statki.has_key(i):
    print self.statki[target][0],' juz nie ma w relevant secie id',i,' bo sie rozlaczyl'
    self.sendQuitObject(target,i)
    self.statki[target][2].remove(i)    
    
    
 def updateAllSets(self):
  for i in self.statki.keys():
   self.updateRelevantSet(i)  

 def sendNewObject(self,toWhom,targetId):
  self.server.sendto(struct.pack("3i8fi%ss"%len(self.statki[targetId][0]),
    					2, targetId,0, #typ pakietu, id obiektu, id modelu
					self.statki[targetId][1][0],self.statki[targetId][1][1], #pos x,y
					self.statki[targetId][3][0],self.statki[targetId][3][1], #speed x,y
					self.statki[targetId][4][0],self.statki[targetId][4][1], #acc x,y
					self.statki[targetId][5], self.statki[targetId][6],	#rot, roting
					len(self.statki[targetId][0]),self.statki[targetId][0]),self.sockety[toWhom])  #dlugosc nazwy,nazwa obiektu
  print 'wyslalem obiekt ',targetId,' do ',toWhom										

 def sendQuitObject(self,toWhom,targetId):
  self.server.sendto(struct.pack("4i",7,targetId,0,0),self.sockety[toWhom])
  print "wyslalem do ",toWhom," ze ",targetId," sie rozlaczyl"  
  
 def sendNewVar(self,targetId,varId):			#typ zmiennej: 5 - rot, 6 - roting
  try:
   for i in self.statki[targetId][2]:
    self.server.sendto(struct.pack("3if",11,targetId,varId-5,self.statki[targetId][varId]),self.sockety[i])
  except:
	pass
 
 def sendNewVect(self,targetId,vectId):			#typ pakietu: 8 - pos(1), 9 - speed(3), 10 - acc(4)
  try:
   for i in self.statki[targetId][2]:
    self.server.sendto(struct.pack("2i2f",vectId,targetId,self.statki[targetId][{8:1,9:3,10:4}[vectId]][0],self.statki[targetId][{8:1,9:3,10:4}[vectId]][1]),self.sockety[i])
 #   print 'wyslalem do ',self.sockety[i],'pakiet: ',vectId,targetId,self.statki[targetId][{8:1,9:3,10:4}[vectId]][0],self.statki[targetId][{8:1,9:3,10:4}[vectId]][1]
    
  except:
	pass
       
 def changeVar(self,targetId,varId,value):
  if varId+5==6: #roting
   print targetId,' sie rotuje'
   if value>0:
    self.statki[targetId][6]=0.1
   if value<0: 
    self.statki[targetId][6]=-0.1
   if value==0:
    self.statki[targetId][6]=0 
   self.sendNewVar(targetId,6)
  if varId+5==7: #speedchange
   print targetId,' odpala silniki'
   if value>0:
    self.statki[targetId][7]=0.1
   if value<0:
    self.statki[targetId][7]=-0.1
   if value==0:
    self.statki[targetId][7]=0    
   self.sendNewVar(targetId,7) 
  
class updater(threading.Thread):
 def __init__(self,target):   
  self.target=target
  self.running=1
  self.counter=0
  self.thingsToSend=[]
  self.clock=pygame.time.Clock()
  threading.Thread.__init__(self)
 def run(self):
  while self.running:
   time.sleep(0.02)
   for i in self.target.statki.keys():
    self.target.statki[i][8]+=1
    if self.target.statki[i][8]>250:
     self.target.handleQuit(self.target.sockety[i])
    else: 
     self.update(i)
   
   
 def update(self,whichOne):   
#    if self.target.statki[i][6]<>0: #roting(6) - zmienia rot(5)
    self.target.statki[whichOne][5]+=self.target.statki[whichOne][6]
    if self.thingsToSend.count([whichOne,5])<1:
      self.thingsToSend+=[[whichOne,5]]
#    if 1==1: #speedchange(7) - zmienia acc(4->10)
    self.target.statki[whichOne][4][0]=round(self.target.statki[whichOne][7]*math.cos(self.target.statki[whichOne][5]+math.pi/2),2)
    self.target.statki[whichOne][4][1]=round(self.target.statki[whichOne][7]*math.sin(self.target.statki[whichOne][5]+math.pi/2),2)
    # print 'nowy acc: ',self.target.statki[i][4][0],self.target.statki[i][4][1]
    if self.thingsToSend.count([whichOne,10])<1:    
      self.thingsToSend+=[[whichOne,10]]
    if (self.target.statki[whichOne][4][0]<>0 or self.target.statki[whichOne][4][1]<>0): #acc(4) - zmienia speed (3->9)
     self.target.statki[whichOne][3][0]+=round(self.target.statki[whichOne][4][0],2)
     self.target.statki[whichOne][3][1]+=round(self.target.statki[whichOne][4][1],2)
 #    print 'nowy speed: ',self.target.statki[whichOne][3][0],self.target.statki[whichOne][3][1]     
    if self.thingsToSend.count([whichOne,9])<1:
      self.thingsToSend+=[[whichOne,9]]
    if (self.target.statki[whichOne][3][0]<>0 or self.target.statki[whichOne][3][1]<>0): #speed(3) - zmienia pos (1->8)
     self.target.statki[whichOne][1][0]-=round(self.target.statki[whichOne][3][0],2)
     self.target.statki[whichOne][1][1]-=round(self.target.statki[whichOne][3][1],2)
    if self.thingsToSend.count([whichOne,8])<1:     
      self.thingsToSend+=[[whichOne,8]]
#    print 'nowy pos: ',self.target.statki[i][1][0],self.target.statki[i][1][1]          

   
class sender(threading.Thread):
 def __init__(self,target):
  self.target=target
  self.running=1
  threading.Thread.__init__(self)
 def run(self):
  while self.running:
    self.target.target.updateAllSets()
    for i in self.target.thingsToSend:
     if i[1] in [5,6]:	#skalary			#PO WYSLANIU WYJEBYWAC TO CO TRZEBA WYSLAC
      self.target.target.sendNewVar(i[0],i[1])
     if i[1] in [8,9,10]: #wektory 
      self.target.target.sendNewVect(i[0],i[1])
     self.target.thingsToSend.remove(i)  
    time.sleep(0.2)
  
asd=server()
prz=updater(asd)
snd=sender(prz)
prz.start()
snd.start()
asd.run()             
  
#			     0	     1         2	  3      4    5     6      7		8
# statki = {index socketu:[nazwa, [x, y],[relevantSet],[speed],[acc],rot,roting,speedchange, lastPing]}
# sockety = {socket}
# self.db = {nazwa:{'socket':index socketu,'pos':[x,y]}}

