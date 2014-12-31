# This is my first time using Python...so yeah

import socket, sys, random, ConfigParser, time, threading
from crypt import Crypt
from user import User
from functions import Functions

class Penguin(Functions):
	doPrint = False # Set this to TRUE if you want to see all the packets and stuff
	
	user = User()
	cryptObject = Crypt()
	
	def __init__(self):
		print "Welcome to PPCL, a PCL by Gokhan137."
		print "If you encounter any errors, search up the corresponding number in __init__.py to find out where it occurred." + "\n"
		
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
		
	def sendAndWait(self, socket, data, find, error):
		self.debugPrint("Sent: %s" % (data + chr(0)))
	
		socket.send(data + chr(0))
		while True:
			recv = socket.recv(1024)
			if recv.find("%xt%e%") != -1:
				self.handleError(recv)
				break
			elif recv.find(find) != -1:
				break
				
		self.debugPrint("Received: %s from %s" % (recv, error))
			
		return recv
		
	def recvData(self):
		recv = self.s.recv(1024)
		if recv.find("%xt%e%") != -1:
			self.handleError(recv)
			
		return recv
		
	def handleError(self, packet):
		if packet.find("%xt%e%100%200%") != -1:
			pass
		else:
			print "Received error %s \n" % (packet)
			sys.exit()
		
	def pause(self, seconds):
		time.sleep(int(seconds))
		
	def disconnect(self):
		self.s.close()
		self.loggedIn = False
		sys.exit()
		
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
		
	def getBetween(self, data, one, two):
		half = data.split(one)
		half = half[1].split(two)
		self.debugPrint("rndK: %s" % (half[0]))
		return half[0]
		
	def breakPacket(self, packet, breaker):
		packetArr = []
		splitP = packet.split(breaker)
		for i in splitP:
			packetArr.append(i)
		return packetArr
		
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
			sys.exit()
			
		self.s.connect((address , port))
		self.sendAndWait(self.s, "<policy-file-request/>", "<cross-domain-policy>", 1)
		self.sendAndWait(self.s, "<msg t='sys'><body action='verChk' r='0'><ver v='153' /></body></msg>", "apiOK", 2)
		self.rndK = self.sendAndWait(self.s, "<msg t='sys'><body action='rndK' r='-1'></body></msg>", "rndK", 3)
		self.rndK = self.getBetween(self.rndK, "<k>", "</k>")
		
	def findServerInfo(self, server):
		info = []
	
		config = ConfigParser.ConfigParser()
		config.read('servers.ini')
		
		try:
			info.append(config.get(server, 'IP'))
			info.append(config.get(server, 'Port'))
		except:
			print "Didn't find the specified server. Maybe you typed it in wrong? (Note that the first letter has to be uppercase.) \n"
			sys.exit()
		
		return info
		
	def findRoomInt(self, roomID):
		config = ConfigParser.ConfigParser()
		config.read('rooms.ini')
		
		try:
			return config.get(str(roomID), 'Internal')
		except:
			print "There was an error finding the room information. \n"
			sys.exit()
	
	def joinServer(self, server):
		serverInfo = self.findServerInfo(server)
		
		self.handshake(serverInfo[0], int(serverInfo[1]))
		key = self.cryptObject.getGameHash(self.user.loginKey, self.rndK) + self.user.loginKey
		
		self.sendAndWait(self.s, "<msg t='sys'><body action='login' r='0'><login z='w1'><nick><![CDATA["+self.user.userstring+"]]></nick><pword><![CDATA["+key+"#"+self.user.confirmationHash+"]]></pword></login></body></msg>", "%xt%l%-1%", 5)
		
		self.sendAndWait(self.s, "%xt%s%j#js%-1%"+self.user.ID+"%"+self.user.loginKey+"%en%", "%-1%", 6)
		
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
		
		uData = self.sendAndWait(self.s, "<msg t='sys'><body action='login' r='0'><login z='w1'><nick><![CDATA["+username+"]]></nick><pword><![CDATA["+self.cryptObject.getLoginHash(password, self.rndK)+"]]></pword></login></body></msg>", "%xt%l%-1%", 4)
		
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