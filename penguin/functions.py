# This is my first time using Python...so yeah

class Functions(object):
	def sendMessage(self, message):
		self.sendPacket(['s', 'm#sm', self.user.internalRoomID, self.user.ID, message])
	
	def sendPosition(self, x, y):
		self.sendPacket(['s','u#sp', self.user.internalRoomID, x, y])
	
	def joinRoom(self, roomID):
		self.sendPacket(['s', 'j#jr', -1, roomID, 0, 0])
		self.user.internalRoomID = self.findRoomInt(roomID)
	
	def throwSnowball(self, x, y):
		self.sendPacket(['s', 'u#sb', self.user.internalRoomID, x, y])