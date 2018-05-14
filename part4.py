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
				print "*******respData********"
				print respData
				print "***********************"

				if self.getResponseCode(respData) is 0:
					print "sending data back"
					sent = sockUDP.sendto(respData, address)
				elif self.getResponseCode(respData) is 3:
					response = self.createResponse(respData, data)
					print "************NEW RESPONSE: ***************"
					print response
					print "******************************************"
					print "new response length: ", len(response)
					sent = sockUDP.sendto(response, address)
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

	def getResponseCode(self, respData):
		#first 14 bytes is ethernet header
		#next 20 bytes is the ip header
		#what we want to find is bits 23-26, where u get response code.....important is "3": response error
		bitsArray = self.hexToBits(respData)
		print "LENGTH OF RESP IN BITS: ", len(bitsArray)
		respCodeArr = []
		for x in range(28, 32):
			respCodeArr.append(bitsArray[x])

		#print "respCode TEST: ", respCodeArr
		respCode = ""
		for x in respCodeArr:
			respCode += str(x)
		respCode = int(respCode, 2)
		print "respCode: ", respCode
		return respCode

	def hexToBits(self, data):
	    output = []
	    for c in data:
	        bits = bin(ord(c))[2:]
	        bits = '00000000'[len(bits):] + bits
	        output.extend([int(b) for b in bits])
	    return output
		
	def bitsToHex(self, bits):
	    result = []
	    for b in range(len(bits) / 8):
	        byte = bits[b*8:(b+1)*8]
	        result.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
	    return ''.join(result)

	def createResponse(self, respData, data):
		'''
		bitsArray = self.hexToBits(data)
		header = []
		for x in range(0, 96):
			header.append(bitsArray[x])
		header[0] = 1
		for x in range(12, 16):
			header[x] = 0
		headerHex = self.bitsToHex(header)
		'''
		bitsArray = self.hexToBits(respData)
		header = []
		for x in range(0, 96):
			header.append(bitsArray[x])
		for x in range(17+16+1-3, 17+16+1):
			header[x] = 0
		headerHex = self.bitsToHex(header)

		#request header is 12 bytes -> 96 bits, so we just want the rest of it
		nameField = data[12:]

		
		rType = self.bitsToHex('00000001')
		rClass = self.bitsToHex('00000001')
		TTL = self.bitsToHex('1000')

		myHostname = socket.gethostname()
		myAddr = socket.gethostbyname(myHostname)
		dotlessAddr = myAddr.split(".")
		myAddrHex = self.bitsToHex(dotlessAddr)
		rLength = '0004'

		response = headerHex + nameField + rType + rClass + TTL + rLength + myAddrHex
		return response

if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
