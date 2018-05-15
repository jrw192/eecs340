#!/usr/bin/env python 

import socket, os, datetime, sys

class HttpServer:
	def __init__(self):
		self.port = 80 #default
		self.s = None

	def httpServer(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to the port and listen for connections 
		self.s.bind(("", self.port))
		self.s.listen(1)
		
		while True:
			#part A: accept a new connection
			connSocket, address = self.s.accept()
			print "socket address: ", address

			#part B: read HTTP request from connectionSocket and parse it
			request = connSocket.recv(1024)
			print "**request**"
			print request
			print "***********"

			requestedFile = self.getReqFile(request)
			print "**requested file: ", requestedFile

			hostName = (self.getHost(request)).strip()
			print "**hostname: ", hostName
			absFile = str(os.path.abspath(requestedFile)).strip()
			if self.isHostValid(hostName) and os.path.isfile(absFile):
				#construct HTTP response if file exists
				fileContent = ""
				print "opening file...."
				file = open(absFile, "rb")
				fileContent = file.read()
				file.close()
				headerContent = self.makeHeader(requestedFile)
				print "***header***"
				print headerContent
				print "************"
				#print "***fileContent"
				#print fileContent
				#print "************"
				connSocket.send((headerContent + fileContent))
				#close when done
				self.s.close()

			else:
				print "we made our own page"
				self.writeOurFile(hostName)
				
				date = datetime.datetime.now()
				date = date.strftime("%d/%m/%Y %H:%M:%S")
				dateResponse = "Date: " + date + "\r\n"
				typeResponse = "Content-Type: text/html\r\n"
				headerContent = "HTTP/1.1 200 OK\r\n" + dateResponse + typeResponse

				file = open("ourFile", "rb")
				fileContent = file.read()
				file.close()

				connSocket.send((headerContent + fileContent))
				self.s.close()


	def makeHeader(self, requestedFile):
		date = datetime.datetime.now()
		date = date.strftime("%d/%m/%Y %H:%M:%S")
		dateResponse = "Date: " + date + "\r\n"
		typeResponse = "Content-Type: text/html\r\n"
		headerContent = dateResponse + typeResponse
		
		print os.path.abspath(requestedFile)
		print len(str(os.path.abspath(requestedFile)).strip())
		print len('/home/jrw192/project1/rfc2616.html')
		#if "htm" not in requestedFile:
		#	headerContent = "HTTP/1.1 403 Forbidden\r\n" + headerContent
		if os.path.isfile(str(os.path.abspath(requestedFile)).strip()):	#this works on murphy
			#print "byteArray: ", list(bytearray((os.path.abspath(requestedFile).strip())))
			headerContent = "HTTP/1.1 200 OK\r\n" + headerContent
		else: 
			headerContent = "HTTP/1.1 404 Not Found\r\n" + headerContent
			# call writeOurFile when page not found?? what james did 
		headerContent.encode()
		return headerContent

	def getReqFile(self, request):
		requestedFile = request[request.find(' /')+len(' /'):request.find('HTTP')]
		return requestedFile

	def getHost(self, request):
		hostName = request[request.find('Host: ')+len('Host: '):request.find('Connection')]
		return hostName

	def isHostValid(self, hostname):
		try:
			socket.gethostbyname(hostname)
			return True
		except socket.error:
			return False

	
	def writeOurFile(self, hostName):
		file = open("ourFile", "w")
		pageContent = """<!DOCTYPE html> 
		<html> 
		<body> 
		<p> I see that you were looking for """ + hostName + """, but wouldn't you rather
		buy that from <a href = "google.com"> google.com </a>? </p> 
		</body> 
		</html>"""
		file= open("ourFile","w")
		file.write(pageContent)
		file.close()


if  __name__ =='__main__':  
	s = HttpServer() 
	#print "args: ", sys.argv
	s.httpServer()
