#!/usr/bin/env python3

import socket
import sys
import select
import json

import pickle
import rsa






def client(name, host, port):
	
	
	def initalServerConnection(host, port):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))
		
		return s
		

	
	def giveServerCredentials(name):
		
		(publicKey, privateKey) = createKeys()
		
		pickledPublicKey = pickle.dumps(publicKey,0).decode()
		
		messageDictionary = {
			"destName": "CONNECTEDUSERNAME",
			"message": name + "-" + pickledPublicKey
		}
		
		
		messageJson = json.dumps(messageDictionary)
		
		
		serverConnection.send(messageJson.encode())
		
		return privateKey
		
		
		
	def createKeys():
		
		(public, private) = rsa.newkeys(1600, poolsize=2)
		
		return (public, private)
	
	def decryptData(data, private):
		return rsa.decrypt(data, private)
	
	def askServer(message):
		messageDictionary = {
			"destName": message,
			"message": message
		}
		
		messageJson = json.dumps(messageDictionary)
		
		
		serverConnection.send(messageJson.encode())
		
		
	serverConnection = initalServerConnection(host, port)


	privateKey = giveServerCredentials(name)
	

	inputs = [serverConnection, sys.stdin]
	
	kill = False
	
	
	
	while kill != True:
		
		readable, _, _ = select.select(inputs, [], [])
		
		for reader in readable:

			if reader is serverConnection:
				
					data = reader.recv(1000)
					
					if data:
						
						
						decryptedJson = decryptData(data, privateKey)

						jsonData = json.loads(decryptedJson.decode())
						
						try:
							
							messages = jsonData["messages"]
							
						except Exception as e:
							messages = [jsonData]
							
						for message in messages:
							
							fromName = message["from"]
							
							
							print("<{}> {}".format(fromName, message["message"])) 
							
							if (fromName == "SERVERTERM"):
								kill = True
				
			else:
				
				inputStripped = sys.stdin.readline().rstrip()
				
				if (inputStripped.startswith("GETUSERS")):
					
					askServer("GETUSERS")
				
				elif (inputStripped.startswith("LEAVE")): 
					askServer("LEAVE")
					
				else:
					
					try:
						
						split = inputStripped.split(sep="-")
						
						userDest = split[0]
						message = split[1]
						
					except:
						userDest = "EVERYONE"
						message = inputStripped
					
					messageDictionary = {
						"destName": userDest,
						"message": message
					}
					
					messageJson = json.dumps(messageDictionary)
					
					
					serverConnection.send(messageJson.encode())
					

	serverConnection.close()

def main():
	name = input("What is your name: ")
	host = ''
	port = 9002
	client(name, host, port)
	
if __name__ == '__main__':
	
	
	main()
	