# This is my first time using Python...so yeah

import hashlib

class Crypt(object):
	def md5(self, string):
		return hashlib.md5(string).hexdigest()
		
	def encryptPassword(self, password):
		hashedPass = self.md5(password)
		hashedPass = hashedPass[16:] + hashedPass[:16]
		return hashedPass
		
	def getLoginHash(self, password, random_key):
		primary = self.encryptPassword(password).upper()
		append = 'a1ebe00441f5aecb185d0ec178ca2305Y(02.>\'H}t":E1_root'
		secondary = primary + random_key + append
		last = self.encryptPassword(secondary)
		return last
		
	def getGameHash(self, login_key, random_key):
		hash = self.md5(login_key + random_key)
		hash = hash[16:] + hash[:16]
		return hash