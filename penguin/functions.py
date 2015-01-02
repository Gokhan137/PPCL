# This is my first time using Python...so yeah

from packetParse import PacketParse

class Functions(PacketParse):
	def sendMessage(self, message):
		self.sendPacket(['s', 'm#sm', self.user.internalRoomID, self.user.ID, message])
	
	def sendPosition(self, x, y):
		self.sendPacket(['s','u#sp', self.user.internalRoomID, x, y])
	
	def joinRoom(self, roomID):
		self.sendPacket(['s', 'j#jr', -1, roomID, 0, 0])
	
	def throwSnowball(self, x, y):
		self.sendPacket(['s', 'u#sb', self.user.internalRoomID, x, y])
	
	def getPlayerByName(self, username):
		self.sendPacket(['s', 'u#pbn', -1, username])
	
	def findBuddy(self, penguinID):
		self.sendPacket(['s', 'u#bf', -1, penguinID])