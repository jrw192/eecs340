import socket, sys, select, Queue

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamAddr = ('8.8.8.8', 53)

	def dns_proxy(self):
		sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockUDP.bind(("0.0.0.0", self.port))
	
		sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sockTCP.bind(("0.0.0.0", self.port))
		sockTCP.listen(5)
		inputs = [ sockUDP, sockTCP ]
		outputs = [ ] #we don't actually need this, just placeholder

		while inputs:
			readable, writable, exceptional = select.select(inputs, outputs, inputs)
			for s in readable:
				if s is sockUDP:
					print "using udp to listen"
					self.UDP(s)
					print "DONE"
				elif s is sockTCP:
					print "using tcp to listen"
					self.TCP(s)
					print "DONE"


	def UDP(self, sockUDP):
		data, address = sockUDP.recvfrom(4096)
		if data:
			print "received ", len(data), " bytes from ", address
			print "addr: ", address, " data length: ", len(data)
			
			upstreamSockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			upstreamSockUDP.connect(self.upstreamAddr)

			upstreamSockUDP.send(data)
			print "wait for a response from upstream"
			respData, respAddr = upstreamSockUDP.recvfrom(4096)
			#print "we got our response data, response length: ", len(respData)
			if respData:
				#print "*******respData bit version********"
				#print self.toBits(respData)
				#print "***********************"
				#print "bits data length: ", len(self.toBits(respData))
				print "******************respData: "
				print str(respData)
				print "*****************************"

				print "sending data back"
				sent = sockUDP.sendto(respData, address)
			upstreamSockUDP.close()

	def TCP(self, sockTCP):

		connSocket, address = sockTCP.accept()
		data, __ = connSocket.recvfrom(4096)
		if data:
			print "received ", len(data), " bytes from ", address

			upstreamSockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				upstreamSockTCP.connect(self.upstreamAddr)
				print "connected upstreamSockTCP"
			except:
				print "upstreamSockTCP failed to connect. error: ", socket.error

			upstreamSockTCP.send(data)
			respData, respAddr = upstreamSockTCP.recvfrom(4096)
			print "we got our response data, response length: ", len(respData)
			if respData:
				print "sending response data back"
				sockTCP.sendto(respData, address)
			upstreamSockTCP.close()

	def parseResponse(self, type, respData):
		#first 14 bytes is ethernet header
		#next 20 bytes is the ip header
		#what we want to find is bits 23-26, where u get response code.....important is "3": response error
		bitsArray = self.toBits(respData)
		print "LENGTH OF RESP IN BITS: ", len(bitsArray)
		header = []
		for x in range(0, 32):
			header.append(bitsArray[x])
		print "*****HEADER****"
		print header
		print "***************"
		print "header length: ", len(header)

		respCodeArr = []
		for x in range(28, 32):
			respCodeArr.append(bitsArray[x])

		print "respCode TEST: ", respCodeArr
		respCode = ""
		for x in respCodeArr:
			respCode += str(x)
		respCode = int(respCode, 2)
		print "respCode: ", respCode



	#def constructResponse(self):



	def toBits(self, data):
	    output = []
	    for c in data:
	        bits = bin(ord(c))[2:]
	        bits = '00000000'[len(bits):] + bits
	        output.extend([int(b) for b in bits])
	    return output
		
	#def createRepsonse(self, )



if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
