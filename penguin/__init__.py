# This is my first time using Python...so yeah

import socket, sys, random, ConfigParser, time, threading
from crypt import Crypt
from user import User
from functions import Functions

class Penguin(Functions):
	doPrint = False # Set this to TRUE if you want to see all the packets and stuff
	
	user = User()
	cryptObject = Crypt()
	listeners = {}
	
	def __init__(self):
		print "Welcome to PPCL, a PCL by Gokhan137."
		print "If you encounter any errors, search up the corresponding number in __init__.py to find out where it occurred." + "\n"
		self.addListener("jr", self.changeIntRoomID)
		
	def die(self):
		sys.exit()
		
	def addListener(self, string, func):
		self.listeners[string] = func
		
	def changeIntRoomID(self, packet):
		self.user.internalRoomID = packet[2]
		
	def debugPrint(self, statement):
		if self.doPrint == True:
			print statement + "\n"
		else:
			pass

	def generateAddress(self):
		addresses = ["204.75.167.218", "204.75.167.219", "204.75.167.176", "204.75.167.177"]
		self.loginAddress = random.choice(addresses)
		
		ports = [6112, 3724]
		self.loginPort = random.choice(ports)
		
	def sendAndWait(self, data, find, error):
		self.debugPrint("Sent: %s" % (data + chr(0)))
	
		self.s.send(data + chr(0))
		while True:
			recv = self.recvData(False)
			if recv.find(find) != -1:
				break
				
		self.debugPrint("Received: %s from %s" % (recv, error))
			
		return recv
		
	def recvData(self, doLoop = True):
		recvRaw = self.s.recv(1024)
		
		if recvRaw.find("%xt%e%") != -1 and recvRaw.find("%xt%e%100%200%") == -1:
			self.handleError(recvRaw)
		if doLoop == True:
			for i in self.listeners:
				if recvRaw.find("%" + i + "%") != -1:
					recv = self.breakPacket(recvRaw, chr(0))

					for item in recv:
						if item.find("%" + i + "%") != -1:
							recv = self.breakPacket(item, "%")
							recv.pop(0)
							recv.pop()
							self.listeners[i](recv)
		return recvRaw
		
	def handleError(self, packet):
		if packet.find("%xt%e%100%200%") != -1:
			pass
		else:
			print "Received error %s \n" % (packet)
			self.die()
		
	def pause(self, seconds):
		time.sleep(int(seconds))
		
	def disconnect(self):
		print "Disconnecting in 3 seconds... \n"
		self.pause(3)
		self.s.close()
		self.loggedIn = False
		self.die()
		
	def heartbeat(self):
		while self.loggedIn == True:
			self.pause(60)
			if self.loggedIn == True: # You know, cause a lot can happen within 60 seconds
				self.sendPacket(["s", "u#h", 2])
			else:
				print "Stopped sending heartbeat packet. \n"
				break
		else:
			print "Stopped sending heartbeat packet. \n"
				
	def recvThread(self):
		while self.loggedIn == True:
			data = self.recvData()
			if not data:
				print "Lost connection! \n"
				self.loggedIn = False
				break
			else:
				if self.doPrint == True:
					print data + "\n"
		else:
			print "We ain't getting anything now. You disconnected! \n"
		
	def sendPacket(self, packet):
		pack = "%xt"
		for i in packet:
			pack += "%" + str(i)
		pack += "%" + chr(0)
		self.debugPrint("Sent: " + pack)
		self.s.send(pack)
		
	def handshake(self, address, port):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			print "There was an error creating the socket. \n"
			self.die()
			
		self.s.connect((address , port))
		self.sendAndWait("<policy-file-request/>", "<cross-domain-policy>", 1)
		self.sendAndWait("<msg t='sys'><body action='verChk' r='0'><ver v='153' /></body></msg>", "apiOK", 2)
		self.rndK = self.sendAndWait("<msg t='sys'><body action='rndK' r='-1'></body></msg>", "rndK", 3)
		self.rndK = self.getBetween(self.rndK, "<k>", "</k>")
		
	def findServerInfo(self, server):
		info = []
	
		config = ConfigParser.ConfigParser()
		config.read('ini/servers.ini')
		
		try:
			info.append(config.get(server, 'IP'))
			info.append(config.get(server, 'Port'))
		except:
			print "Didn't find the specified server. Maybe you typed it in wrong? (Note that the first letter has to be uppercase.) \n"
			self.die()
		
		return info
	
	def joinServer(self, server):
		serverInfo = self.findServerInfo(server)
		
		self.handshake(serverInfo[0], int(serverInfo[1]))
		key = self.cryptObject.getGameHash(self.user.loginKey, self.rndK) + self.user.loginKey
		
		self.sendAndWait("<msg t='sys'><body action='login' r='0'><login z='w1'><nick><![CDATA["+self.user.userstring+"]]></nick><pword><![CDATA["+key+"#"+self.user.confirmationHash+"]]></pword></login></body></msg>", "%xt%l%-1%", 5)
		
		self.sendAndWait("%xt%s%j#js%-1%"+self.user.ID+"%"+self.user.loginKey+"%en%", "%-1%", 6)
		
		self.loggedIn = True
		
		heartbeatVar = threading.Thread(target=self.heartbeat, args=[])
		heartbeatVar.daemon = True
		heartbeatVar.start()
		
		recvThreadVar = threading.Thread(target=self.recvThread, args=[])
		recvThreadVar.daemon = True
		recvThreadVar.start()

	def login(self, username, password, server):
		self.generateAddress()
		
		self.handshake(self.loginAddress, self.loginPort)
		
		uData = self.sendAndWait("<msg t='sys'><body action='login' r='0'><login z='w1'><nick><![CDATA["+username+"]]></nick><pword><![CDATA["+self.cryptObject.getLoginHash(password, self.rndK)+"]]></pword></login></body></msg>", "%xt%l%-1%", 4)
		
		print "\n" + "Welcome to Club Penguin!" + "\n"
		
		packetElements = self.breakPacket(uData, "%")
		userData = self.breakPacket(packetElements[4], "|")
		
		self.user.ID = userData[0]
		self.user.confirmationHash = packetElements[5]
		self.user.friendsKey = packetElements[6]
		self.user.SWID = userData[1]
		self.user.username = userData[2]
		self.user.loginKey = userData[3]
		self.user.userstring = packetElements[4]
		self.user.x = 0
		self.user.y = 0
		
		self.debugPrint("ID: " + self.user.ID)
		self.debugPrint("Confirmation Hash: " + self.user.confirmationHash)
		self.debugPrint("Friends Key: " + self.user.friendsKey)
		self.debugPrint("SWID: " + self.user.SWID)
		self.debugPrint("Username: " + self.user.username)
		self.debugPrint("Login Key: " + self.user.loginKey)
		self.debugPrint("User String: " + self.user.userstring)
		
		self.s.close()
		
		self.joinServer(server)