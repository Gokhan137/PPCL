# This is my first time using Python...so yeah

from penguin import Penguin

penguin = Penguin()
username = raw_input("Username: ")
password = raw_input("Password: ")
server = raw_input("Server: ")

penguin.login(username, password, server)

follow = raw_input("Name of penguin you want to follow: ")

def onPBN(packet):
	penguin.followID = packet[4]
	
def onSP(packet):
	if packet[3] == penguin.followID:
		penguin.sendPosition((int(packet[4]) - 40), packet[5])
		
def onBF(packet):
	if packet[3] == -1:
		print follow + " went offline!"
		penguin.die()
	else:
		penguin.joinRoom(packet[3])
		
def onRP(packet):
	if packet[3] == penguin.followID:
		penguin.findBuddy(penguin.followID)

penguin.addListener("pbn", onPBN)

penguin.getPlayerByName(follow)

while True:
	try:
		penguin.followID
		break
	except:
		penguin.pause(1)

penguin.addListener("sp", onSP)
penguin.addListener("rp", onRP)
penguin.addListener("bf", onBF)

penguin.findBuddy(penguin.followID)

while True: # Keeps the heartbeat and recv threads running if you decide not to disconnect
	penguin.pause(999)