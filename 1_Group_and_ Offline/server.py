#!/usr/bin/env python3

import socketserver as ss
import json


class ServerThreader(ss.ThreadingMixIn, ss.TCPServer):
	pass


class Server(ss.StreamRequestHandler):

#	key: address ... val: serverobject
	clients = dict()

#	key: name ... val: address
	usernames = dict()

	#	key: name ... val: [messageDict]	
	offlineMessages = dict()

	def createMessageDict(self, source, data):
		messageDictionary = {
			"from" : source,
			"message" : data
		}

		return messageDictionary

	def sendEveryoneMessage(self, messageDictionary, myAddr):
		
		
		
		messageJson = json.dumps(messageDictionary)
		
		for addr, client in self.clients.items():		
		
			if (addr != myAddr):
				client.request.sendall(messageJson.encode())


	def sendExternalMessage(self, destAddr, messageDictionary):



		messageJson = json.dumps(messageDictionary)
		reciever = self.clients[destAddr]
		reciever.request.sendall(messageJson.encode())
		
	def sendDictionary(self, dict):
		thisJson = json.dumps(dict)
		
		
		self.request.sendall(thisJson.encode())
		
		

	def systemResponse(self, message):
		messageDictionary = {
			"from" : "SERVER",
			"message" : message
		}
		self.sendDictionary(messageDictionary)
		


	def remove(self, connectionAddr, name):
		res1 = self.clients.pop(connectionAddr, None)
		res2 = self.usernames.pop(name, None)


		messageDictionary = {
			"from" : "SERVERTERM",
			"message" : "Have a great day!"
		}
		self.sendDictionary(messageDictionary)

	def handle(self):
		while True:

			peerName = self.request.getpeername()
			fromAddr = peerName[1]


			self.data = self.request.recv(1024)


			jsonData = json.loads(self.data.decode())

			message = jsonData["message"]
			dest = jsonData["destName"]


			if (dest.startswith("CONNECTEDUSERNAME")):

				name = message

				try:
						# add self to clients list
						self.clients[fromAddr] = self
						# add self to usernames list
						self.usernames[name] = fromAddr

						print(fromAddr, "with username,", name , "just connected to the server.")

				except Exception as e:
					print("ERROR")
					print(e)

				response = "Welcome to ClassChat, " + name + ".\n\tTo send a message use the format \"USERNAME-MESSAGE\" " + "\n\t Type GETUSERS to view all users."
				
				try:
					offline = self.offlineMessages.pop(name)
					
					self.sendDictionary({ "messages" : offline})
					
					
						
					
				except KeyError as e:
					self.systemResponse(response)

			elif(dest == "LEAVE"):

				myAddr = fromAddr
				myName = list(self.usernames.keys())[list(self.usernames.values()).index(fromAddr)]

				print("Deleting user,", fromAddr, "with username,", myName, "from server.")

				self.remove(myAddr, myName)

			elif (dest.startswith("GETUSERS")):
				message = ""
				self.usernames.keys()
				for key in sorted(self.usernames.keys()):
					message += ("\n" + key)

				self.systemResponse(message)
			
			elif (dest.startswith("EVERYONE")):
				myName = list(self.usernames.keys())[list(self.usernames.values()).index(fromAddr)]
				messageDict = self.createMessageDict(myName, message)
				
				
				self.sendEveryoneMessage(messageDict, fromAddr)
				
				self.systemResponse(("Sent message to " + dest))

			else:
				#actual message
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




if __name__ == '__main__':


	host = ""
	port = 9003
	thisServerThreader = ServerThreader((host,port), Server)

	print("Started: " , thisServerThreader)

	thisServerThreader.serve_forever()
	