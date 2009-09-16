#!/usr/local/bin/python
import socket,threading,pygame,select,os,sys,struct,math,time,curses,operator


def dictIndex(whereToLook,whatToFind):
    for i in whereToLook.items():
        if i[1]==whatToFind:
            return i[0]
    if whereToLook.values().count(whatToFind)==0:
        return 0

class server:
    def __init__(self):
        self.server=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.server.bind(("",int(sys.argv[1])))
#  self.server.listen(5)
        self.botsAmt=0
        self.sockety={0:sys.stdin,1:self.server}
        self.accounts={'asdf':'asdf',
                       'qwer':'qwer',
                       'zxcv':'zxcv'
                      }
        self.db={'asdf':{'socket':None,'pos':[100,100],'model':0},
                 'qwer':{'socket':None,'pos':[150,100],'model':0},
                 'zxcv':{'socket':None,'pos':[1500,1500],'model':0},
                 'bot0':{'socket':None,'pos':[200,220],'model':0},
                 'bot1':{'socket':None,'pos':[240,330],'model':0},
                 'bot2':{'socket':None,'pos':[280,440],'model':0},
                 'bot3':{'socket':None,'pos':[320,1550],'model':1},
                 'bot4':{'socket':None,'pos':[360,660],'model':0},
                 'bot5':{'socket':None,'pos':[400,770],'model':1},
                 'Solar plant':{'model':1}
                }
        self.running=1
        self.statki={}
        self.stacje={}
        self.makeStations()
        self.makeBots(2)


    def makeBots(self,howMany):
        for i in range(howMany):
            tempId=max(self.sockety.keys())+1
            self.sockety[tempId]=('0.0.0.0',self.botsAmt+1)
            self.statki[tempId]=['bot%s'%i,[self.db['bot%s'%i]['pos'][0],self.db['bot%s'%i]['pos'][1]],[],[0,0],[0,0],0,0,0,0]
            self.botsAmt+=1

    def makeStations(self):
        tempId=max(self.sockety.keys())+1
        self.sockety[tempId]=('0.0.0.0',self.botsAmt+1)
        self.statki[tempId]=['Solar plant',[1000,1000],[],[0,0],[0,0],0,0,0,0]
        self.stacje[tempId]=[0,{0:1000,1:15},0,[]]


    def run(self):
        while self.running:
            self.input,self.output,self.exc=select.select([sys.stdin,self.server],[],[],0.1)
            for s in self.input:
                if s==self.server:
                    self.data,self.adres=self.server.recvfrom(1024)
                    if self.sockety.values().count(self.adres)==0:
                        self.sockety[max(self.sockety.keys())+1]=self.adres

                    self.typ=struct.unpack('i',self.data[:4])[0]

                    if self.typ==0:
                        self.arg1,self.arg2=struct.unpack('2i',self.data[4:12])
                        self.login,self.pwd = self.data[12:12+self.arg1], self.data[12+self.arg1:12+self.arg1+self.arg2]
                        if self.login == '' or self.pwd == '':
                            self.handleQuit(self.adres)
                        else:
#        print self.login,self.pwd
                            self.handleLogin(self.adres,self.login,self.pwd)

                    if self.typ==11:
                        self.changeVar(dictIndex(self.sockety,self.adres),*struct.unpack('2i',self.data[4:12]))

                    if self.typ==3:
                        self.statki[dictIndex(self.sockety,self.adres)][8]=0
                        self.server.sendto(struct.pack('i',3,)+self.data[4:12],self.adres)

#     if self.typ==12:
#      txt = self.data[16:16+self.arg1]
#      print("ID:%d Chat type %d (Len:%d) : %s" % (self.id, self.arg2, self.arg1, txt))
#      self.consoleAdd(self.adres, "Wiem ze wpisales: %s" % txt)

                    if self.typ==13:
                        self.shootMissile(dictIndex(self.sockety,self.adres))
		    
		    if self.typ==14:
		     self.handleDock(dictIndex(self.sockety,self.adres),*struct.unpack('i',self.data[4:8]))

		


                if s==sys.stdin:
                    pass
# def handleChat(self, sock, )

    def shootMissile(self,shooter):
        for i in self.statki[shooter][2]:
            self.server.sendto(struct.pack('4i',13,shooter,self.statki[shooter][5],0),self.sockety[i])
    
    def handleDock(self,shipId,stationId):
     if self.stacje.has_key(stationId):
      if ((self.statki[shipId][1][0]-self.statki[stationId][1][0])**2 + (self.statki[shipId][1][1]-self.statki[stationId][1][1])**2 < 400) and (self.statki[shipId][3][0]**2 + self.statki[shipId][3][1]**2 < 1):
	  self.server.sendto(struct.pack('2i',14,0),self.sockety[shipId])
	  self.statki[shipId][3][0]=0.0
	  self.statki[shipId][3][1]=0.0
	  self.statki[shipId][4][0]=0.0
	  self.statki[shipId][4][1]=0.0
	  self.sendNewVect(shipId,9)
	  self.sendNewVect(shipId,10)	  





    def consoleAdd(self, addr, txt, logtype=0):
#  print 'wiem ze dodac do konsoli klienta'
        self.server.sendto(struct.pack('4i', 12, self.id, len(txt), logtype) + txt, self.adres)

    def handleLogin(self,sock,login,pwd):
#  print 'bedzie login'
        if self.accounts.has_key(login):
            if self.accounts[login]==pwd and self.db[login]['socket']==None:
                self.db[login]['socket']=dictIndex(self.sockety,sock)
                self.statki[dictIndex(self.sockety,sock)]=[login,[self.db[login]['pos'][0],self.db[login]['pos'][1]],[],[0,0],[0,0],0,0,0,0]
                self.server.sendto(struct.pack('4i',0,dictIndex(self.sockety,sock),self.db[login]['pos'][0],self.db[login]['pos'][1]),sock)
                self.updateAllSets()
#    print login,' sie zalogowal'
            else:
                self.server.sendto(struct.pack('4i',0,0,0,0),sock)
        else:
            self.server.sendto(struct.pack('4i',0,0,0,0),sock)



    def handleQuit(self,sock):
#  print "kogos wyjebalo"
        try:
            self.db[self.statki[dictIndex(self.sockety,sock)][0]]['socket']=None
            self.statki.pop(dictIndex(self.sockety,sock))
#   print self.statki
        except:
            pass
#   print 'wyjebalo kogos kto sie nie zalogowal'
        self.sockety.pop(dictIndex(self.sockety,sock))
        self.updateAllSets()
        self.server.sendto(struct.pack('4i',666,666,666,666),sock)


    def updateRelevantSet(self,target):
        for i in self.statki.keys():
            if self.statki[target][2].count(i)==0 and (self.statki[target][1][0]-self.statki[i][1][0])**2+(self.statki[target][1][1]-self.statki[i][1][1])**2<360000:
#    print self.statki[target][0],' ma w relevant secie ',self.statki[i][0]
                self.statki[target][2].append(i)
                self.sendNewObject(target,i)
            if self.statki[target][2].count(i)>0 and ((self.statki[target][1][0]-self.statki[i][1][0])**2+(self.statki[target][1][1]-self.statki[i][1][1])**2>360000):
#    print self.statki[target][0],' juz nie ma w relevant secie ',self.statki[i][0]
                self.statki[target][2].remove(i)
                self.statki[i][2].remove(target)		
        for i in self.statki[target][2]:
            if not self.statki.has_key(i):
#    print self.statki[target][0],' juz nie ma w relevant secie id',i,' bo sie rozlaczyl'
                self.sendQuitObject(target,i)
                self.statki[target][2].remove(i)


    def updateAllSets(self):
        for j in self.statki.keys():
            self.updateRelevantSet(j)

    def sendNewObject(self,toWhom,targetId):
#  print 'wysylam do: ',self.sockety[toWhom]
        if self.sockety[toWhom][0][0]!='0':
            self.server.sendto(struct.pack("3i8fi%ss"%len(self.statki[targetId][0]),
                                                 2, targetId,self.db[self.statki[targetId][0]]['model'], #typ pakietu, id obiektu, id modelu
                                                 self.statki[targetId][1][0],self.statki[targetId][1][1], #pos x,y
                                                 self.statki[targetId][3][0],self.statki[targetId][3][1], #speed x,y
                                                 self.statki[targetId][4][0],self.statki[targetId][4][1], #acc x,y
                                                 self.statki[targetId][5], self.statki[targetId][6],     #rot, roting
                                                 len(self.statki[targetId][0]),self.statki[targetId][0]),self.sockety[toWhom])  #dlugosc nazwy,nazwa obiektu
#  print 'wyslalem obiekt ',targetId,' do ',toWhom

    def sendQuitObject(self,toWhom,targetId):
        self.server.sendto(struct.pack("4i",7,targetId,0,0),self.sockety[toWhom])
#  print "wyslalem do ",toWhom," ze ",targetId," sie rozlaczyl"

    def sendNewVar(self,targetId,varId):                   #typ zmiennej: 5 - rot, 6 - roting
        try:
            for i in self.statki[targetId][2]:
                self.server.sendto(struct.pack("3if",11,targetId,varId-5,self.statki[targetId][varId]),self.sockety[i])
        except:
            pass

    def sendNewVect(self,targetId,vectId):                 #typ pakietu: 8 - pos(1), 9 - speed(3), 10 - acc(4)
        try:
            for i in self.statki[targetId][2]:
                self.server.sendto(struct.pack("2i2f",vectId,targetId,self.statki[targetId][{8:1,9:3,10:4}[vectId]][0],self.statki[targetId][{8:1,9:3,10:4}[vectId]][1]),self.sockety[i])
    #   print 'wyslalem do ',self.sockety[i],'pakiet: ',vectId,targetId,self.statki[targetId][{8:1,9:3,10:4}[vectId]][0],self.statki[targetId][{8:1,9:3,10:4}[vectId]][1]

        except:
            pass

    def changeVar(self,targetId,varId,value):
        if varId+5==6: #roting
#   print targetId,' sie rotuje'
            if value>0:
                self.statki[targetId][6]=0.1
            if value<0:
                self.statki[targetId][6]=-0.1
            if value==0:
                self.statki[targetId][6]=0
            self.sendNewVar(targetId,6)
        if varId+5==7: #speedchange
#   print targetId,' odpala silniki'
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
            self.counter+=1
            if self.counter==50:
                self.counter=0
                for i in self.target.stacje.keys():
                    self.stationUpdate(i)
            for i in self.target.statki.keys():
                if self.target.sockety[i][0][0]!='0':
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
        self.target.statki[whichOne][4][0]=round(self.target.statki[whichOne][7]*math.cos(self.target.statki[whichOne][5]+math.pi/2),2)
        self.target.statki[whichOne][4][1]=round(self.target.statki[whichOne][7]*math.sin(self.target.statki[whichOne][5]+math.pi/2),2)
        if self.thingsToSend.count([whichOne,10])<1:
            self.thingsToSend+=[[whichOne,10]]
        if (self.target.statki[whichOne][4][0]<>0 or self.target.statki[whichOne][4][1]<>0): #acc(4) - zmienia speed (3->9)
            self.target.statki[whichOne][3][0]+=round(self.target.statki[whichOne][4][0],2)
            self.target.statki[whichOne][3][1]+=round(self.target.statki[whichOne][4][1],2)
            if self.thingsToSend.count([whichOne,9])<1:
                self.thingsToSend+=[[whichOne,9]]
        if (self.target.statki[whichOne][3][0]<>0 or self.target.statki[whichOne][3][1]<>0): #speed(3) - zmienia pos (1->8)
            self.target.statki[whichOne][1][0]-=round(self.target.statki[whichOne][3][0],2)
            self.target.statki[whichOne][1][1]-=round(self.target.statki[whichOne][3][1],2)
            if self.thingsToSend.count([whichOne,8])<1:
                self.thingsToSend+=[[whichOne,8]]

    def stationUpdate(self,whichOne):
        if self.target.stacje[whichOne][0]==0:        #solar plant
            self.target.stacje[whichOne][1][1]+=1

class sender(threading.Thread):
    def __init__(self,target):
        self.target=target
        self.running=1
        threading.Thread.__init__(self)
    def run(self):
        while self.running:
            self.target.target.updateAllSets()
            for i in self.target.thingsToSend:
                if i[1] in [5,6]:  #skalary                        #PO WYSLANIU WYJEBYWAC TO CO TRZEBA WYSLAC
                    self.target.target.sendNewVar(i[0],i[1])
                if i[1] in [8,9,10]: #wektory
                    self.target.target.sendNewVect(i[0],i[1])
                self.target.thingsToSend.remove(i)
            time.sleep(0.2)

class cursesDisplay(threading.Thread):
    def __init__(self,target):
        self.target=target
        self.running=1
        curses.wrapper(self.setStdScr)
        threading.Thread.__init__(self)
    def setStdScr(self,stdscr):
        self.stdscr=stdscr
    def run(self):
        self.stdscr.clear()
        curses.echo()
        curses.curs_set(0)
        self.maxY, self.maxX = self.stdscr.getmaxyx()
        while 1:

            time.sleep(0.5)
            self.stdscr.clear()
            self.stdscr.hline(1,0,'-',self.maxX)
            [self.stdscr.vline(0,i,'|',self.maxY-10) for i in [2,9,15,21,27,33,39,45,49,54,67]]
            [self.stdscr.addstr(0,i,j) for (i,j) in [(0,'id'),(4,'nick'),(10,'pos.x'),(16,'pos.y'),(22,'spd.x'),(28,'spd.y'),
                                                     (34,'acc.x'),(40,'acc.y'),(46,'rot'),(50,'ping'),(55,'Relevant set'),(73,'IP')]]
            for i in self.target.statki.items():
                if i[0]<self.maxY-10:
                    self.stdscr.addstr(i[0],0,str(i[0])[:2])         #id
                    self.stdscr.addstr(i[0],3,i[1][0][:5])           #nick
                    self.stdscr.addstr(i[0],10,str(i[1][1][0])[:5])  #pos.x
                    self.stdscr.addstr(i[0],16,str(i[1][1][1])[:5])  #pos.y
                    self.stdscr.addstr(i[0],22,str(i[1][3][0])[:5])  #spd.x
                    self.stdscr.addstr(i[0],28,str(i[1][3][1])[:5])  #spd.y
                    self.stdscr.addstr(i[0],34,str(i[1][4][0])[:5])  #acc.x
                    self.stdscr.addstr(i[0],40,str(i[1][4][1])[:5])  #acc.y
                    self.stdscr.addstr(i[0],46,str(i[1][5])[:4])     #rot
                    self.stdscr.addstr(i[0],50,str(i[1][8])[:4])     #ping
                    if len(i[1][2])>0:
                        self.stdscr.addstr(int(i[0]),55,reduce(operator.add,[str(j)+' ' for j in i[1][2]])[:13])        #set
                    if self.target.sockety.has_key(i[0]):
                        self.stdscr.addstr(int(i[0]),68,self.target.sockety[i[0]][0][:12])      #ip
            self.stdscr.hline(self.maxY-10,0,'-',self.maxX)
            [self.stdscr.addstr(self.maxY-9,i,j) for (i,j) in [(0,'id'),(5,'Typ'),(29,'Towary'),(60,'Transporty')]]
            self.stdscr.hline(self.maxY-8,0,'-',self.maxX)
            [self.stdscr.vline(self.maxY-10,i,'|',self.maxY) for i in [2,13,50]]

            for i in self.target.stacje.items():
                if i[0]<10:
                    self.stdscr.addstr(self.maxY-9+i[0],0,str(i[0])[:2]) #id
                    self.stdscr.addstr(self.maxY-9+i[0],3,{0:"SolarPlant"}[i[1][0]][:11]) #id
                    self.stdscr.addstr(self.maxY-9+i[0],14,reduce(operator.add,[str(j[1])+{0:'$',1:'EC'}[j[0]]+' ' for j in i[1][1].items()])[:35])

            self.stdscr.refresh()

asd=server()
prz=updater(asd)
snd=sender(prz)
disp=cursesDisplay(asd)
disp.start()
prz.start()
snd.start()
asd.run()

#                            0       1         2          3      4    5     6      7            8
# statki = {index socketu:[nazwa, [x, y],[relevantSet],[speed],[acc],rot,roting,speedchange, lastPing]}
#                               0             1                 2               3
# stacje = {index socketu:[typ stacji,{towarId:[ilosc]},ilosc transportow,[id transportu]]}
#
# sockety = {socket}
# self.db = {nazwa:{'socket':index socketu,'pos':[x,y]}}
