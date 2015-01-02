# This is my first time using Python...so yeah

class PacketParse(object):
	def breakPacket(self, packet, breaker):
		packetArr = []
		splitP = packet.split(breaker)
		for i in splitP:
			packetArr.append(i)
		return packetArr
		
	def getBetween(self, data, one, two):
		half = data.split(one)
		half = half[1].split(two)
		self.debugPrint("rndK: %s" % (half[0]))
		return half[0]