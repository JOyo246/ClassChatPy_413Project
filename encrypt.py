#!/usr/bin/env python3

import json
import pickle

from encrypter import *
from Crypto.Cipher import AES
from Crypto import Random






def encryptMessage(messageDictionary, pubKey):
	
	encodedMessage = json.dumps(messageDictionary).encode()
	
	encryptedMessage = rsa.encrypt(encodedMessage, pubKey)
	
	return encryptedMessage

def decryptMessage(encrypted, private):
	
	decrypted = rsa.decrypt(encrypted, private)
	decoded = decrypted.decode()
	
	jsonString = json.loads(decoded)
	
	
	return jsonString





	
def encrypt(message):
	
	
	encodedMessage = json.dumps(message).encode()
		
	
	raw = _pad(encodedMessage)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(self.key, AES.MODE_CBC, iv)

	
	ciphertext = base64.b64encode(iv + cipher.encrypt(raw.encode()))
	
	return ciphertext

def dictToData(dictMessage):
	
	
	return json.dumps(dictMessage)
	
	
	
	
def main():
	
	
	
#	(public, private) = rsa.newkeys(1024, poolsize=2)
	
	messageDictionary = {
		"from" : "SERVERTERM",
		"message" : "Have a great day!"
	}	
	
	
	key = Random.new().read(40)
	
	
	cipher = AESCipher(key)
	
	messageData = dictToData(messageDictionary)
	
	
	
	encrypted = cipher.encrypt(messageData)
	print(key)
	print("\n\n")
	print(encrypted)
	print("\n\n")
	print(cipher.key)
	
	
#	newMessage = encrypt(messageDictionary)
#	
#	print(newMessage)
	
#	print("encrypted")
#	print(newMessage)
#	
#	print("\n\n\n")
#	decryptedMessage = decryptMessage(newMessage, private)
#	
#	print("decrypted")
#	print(decryptedMessage)
	
if __name__ == "__main__":
	main()