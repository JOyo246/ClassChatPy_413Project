#!/usr/bin/env python3

import socket
import sys
import select
import json

def client(name, host, port):
	
		
	def askServer(message):
		messageDictionary = {
			"destName": message,
			"message": message
		}
		
		messageJson = json.dumps(messageDictionary)
		
		
		s.send(messageJson.encode())
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	
	messageDictionary = {
		"destName": "CONNECTEDUSERNAME",
		"message": name
	}
	messageJson = json.dumps(messageDictionary)
	
	
	s.send(messageJson.encode())
	
	inputs = [s, sys.stdin]
	
	kill = False
	
	while kill != True:
		
		readable, _, _ = select.select(inputs, [], [])
		
		for reader in readable:

			if reader is s:
				
					data = reader.recv(1000)
					
					if data:
						
						jsonData = json.loads(data.decode())
						
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
#				must be keyboard input 
				
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
					
					
					s.send(messageJson.encode())
					
	s.close()
	
	
if __name__ == '__main__':
	
	
	name = input("What is your name?\n Please ensure to not use the \"-\" key and to use a unique name.\nName: ")
	host = ''
	port = 9003
	client(name, host, port)