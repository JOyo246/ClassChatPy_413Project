#!/usr/bin/env python3

import socketserver as ss
import json
import pickle
import rsa

class ServerThreader(ss.ThreadingMixIn, ss.TCPServer):
	pass


class Server(ss.StreamRequestHandler):
	
	
	(serverPublicKey, serverPrivateKey) = rsa.newkeys(1600, poolsize=2)
	

#	key: address ... val: serverobject
	clients = dict()

#	key: name ... val: address
	usernames = dict()

# key:address.... val:pKey
	publicKeys = dict()

	#	key: name ... val: [messageDict]	
	offlineMessages = dict()
	

	def createMessageDict(self, source, data):
		messageDictionary = {
			"from" : source,
			"message" : data
		}

		return messageDictionary
	
	def dumpAndEncodeDict(self, messageDictionary):
		messageJson = json.dumps(messageDictionary)
		encoded = messageJson.encode()
		
		return encoded
		
	def encryptMessageAndSend(self, thisClient, encodedMessage, destAddr):
		
		pubKey = self.publicKeys[destAddr]
		
		encryptedMessage = rsa.encrypt(encodedMessage, pubKey)
		
		print(encodedMessage)
		
		thisClient.request.sendall(encryptedMessage)
		
	def sendEveryoneMessage(self, messageDictionary, myAddr):
		
		for addr, client in self.clients.items():	
						
			if (addr != myAddr):
				
				encoded = self.dumpAndEncodeDict(messageDictionary)
				
				self.encryptMessageAndSend(client, encoded, addr)
				
	def sendExternalMessage(self, destAddr, messageDictionary):

		encoded = self.dumpAndEncodeDict(messageDictionary)
		
		reciever = self.clients[destAddr]
		
		self.encryptMessageAndSend(reciever, encoded, destAddr)
	
	def getMyAddr(self):
		
		peerName = self.request.getpeername()
		myAddr = peerName[1]
		return myAddr

	def systemResponse(self, message):
		messageDictionary = {
			"from" : "SERVER",
			"message" : message
		}
		encodedMessage = self.dumpAndEncodeDict(messageDictionary)
		
		myAddr = self.getMyAddr()
		
		
		self.encryptMessageAndSend(self, encodedMessage, myAddr)


	def remove(self, connectionAddr, name):
		res1 = self.clients.pop(connectionAddr, None)
		res2 = self.usernames.pop(name, None)
		
		messageDictionary = {
			"from" : "SERVERTERM",
			"message" : "Have a great day!"
		}
		encodedMessage = self.dumpAndEncodeDict(messageDictionary)
		
		myAddr = self.getMyAddr()
		
		self.encryptMessageAndSend(self, encodedMessage, myAddr)
	
	
	def sendServerKey(self):
		
		
		pickledPublicKey = pickle.dumps(self.serverPublicKey,0).decode()
		
		messageDictionary = {
			"destName": "SERVERPUBLICKEY",
			"message": pickledPublicKey
		}
		
		send = self.dumpAndEncodeDict(messageDictionary)
		
		
		self.request.sendall(send)
		
		
	def handle(self):
		while True:

			fromAddr = self.getMyAddr()

			self.data = self.request.recv(1024)


			jsonData = json.loads(self.data.decode())

			message = jsonData["message"]
			dest = jsonData["destName"]
			


			if (dest.startswith("CONNECTEDUSERNAME")):
				#wants to join
				
				
				try:
					
					split = message.split(sep="-")
					
					name = split[0]
					
					publicKeyPickledDecoded = split[1]
					
				except Exception as e:
					print("NAme pickle split issue")
					print(e)
					continue
				
				try:
					
					publicKeyPickled = publicKeyPickledDecoded.encode()
					publicKey = pickle.loads(publicKeyPickled)
					
				except Exception as e:
					print("public key depickle issue")
					print(e)
					continue
				
				try:
						# add self to clients list
						self.clients[fromAddr] = self
						# add self to usernames list
						self.usernames[name] = fromAddr
						
						self.publicKeys[fromAddr] = publicKey

						print(fromAddr, "with username,", name , "just connected to the server.")

				except Exception as e:
					print("ERROR")
					print(e)

				response = "Welcome to ClassChat, " + name + ".\n\tTo send a message use the format \"USERNAME-MESSAGE\" " + "\n\t Type GETUSERS to view all users."
				
				try:
					offlineArray = self.offlineMessages.pop(name)
					
					offlineResponse = "Welcome to ClassChat, " + name + ".\n\tTo send a message use the format \"USERNAME-MESSAGE\" " + "\n\t Type GETUSERS to view all users. \n\t Type LEAVE to leave. \n\n Here's what you missed while you were gone..... "
					
					offlineMessage = {
						"from" : "SERVER",
						"message" : offlineResponse
					}
					
					offlineArray.insert(0, offlineMessage)
					
					
					encodedMessage = self.dumpAndEncodeDict({ "messages" : offlineArray})
					
					myAddr = self.getMyAddr()
					
					self.encryptMessageAndSend(self, encodedMessage, myAddr)
					
				except KeyError as e:
					print("No offline messages for", e)
					self.systemResponse(response)

			elif(dest == "LEAVE"):
				#wants to leave
				
				myAddr = fromAddr
				myName = list(self.usernames.keys())[list(self.usernames.values()).index(fromAddr)]

				print("Deleting user,", fromAddr, "with username,", myName, "from server.")

				self.remove(myAddr, myName)

			elif (dest.startswith("GETUSERS")):
				#wants the list of users
				
				message = ""
				self.usernames.keys()
				for key in sorted(self.usernames.keys()):
					message += ("\n" + key)

				self.systemResponse(message)
			
			elif (dest.startswith("EVERYONE")):
				#sending a group message
				
				myName = list(self.usernames.keys())[list(self.usernames.values()).index(fromAddr)]
				messageDict = self.createMessageDict(myName, message)
				
				
				self.sendEveryoneMessage(messageDict, fromAddr)
				
				self.systemResponse(("Sent message to " + dest))

			else:
				#sending a direct message
				myName = list(self.usernames.keys())[list(self.usernames.values()).index(fromAddr)]
				
				messageDict = self.createMessageDict(myName, message)
				
				try:
					destAddr = self.usernames[dest]
					
				except KeyError as e:
					
					
					self.offlineMessages.setdefault(dest, []).append(messageDict)
					
					self.systemResponse("No user available named " +  dest + " ....storing message offline.")
										
					
					continue


				print("Message sent: {} -> {}".format(myName, dest))

				self.sendExternalMessage(destAddr, messageDict)

				self.systemResponse(("Sent message to " + dest))

def main():
	
	
	host = ""
	port = 9003
	thisServerThreader = ServerThreader((host,port), Server)
	
	print("Started: " , thisServerThreader)
	
	thisServerThreader.serve_forever()

if __name__ == '__main__':
	main()


	