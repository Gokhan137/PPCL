# This is my first time using Python...so yeah

from penguin import Penguin

penguin = Penguin()
username = raw_input("Username: ")
password = raw_input("Password: ")
server = raw_input("Server: ")

penguin.login(username, password, server)

penguin.joinRoom(100)
penguin.pause(3)
penguin.sendPosition(300, 250)
penguin.pause(3)
penguin.throwSnowball(400, 200)
penguin.pause(3)
penguin.sendMessage("Goodbye")
penguin.pause(3)
penguin.joinRoom(110)
penguin.pause(5)
penguin.sendMessage("Hello")
penguin.pause(3)
penguin.disconnect()

while True: # Keeps the heartbeat and recv threads running if you decide not to disconnect
	penguin.pause(999)