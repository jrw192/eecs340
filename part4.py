import socket, sys, select, Queue, binascii

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamAddr = ('8.8.8.8', 53)

	def dns_proxy(self, publicIP):
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
				responseCode = self.getResponseCode(respData)

				if responseCode is 0:
					print "sending data back"
					sent = sockUDP.sendto(respData, address)
				elif responseCode is 3:
					response = self.createResponse(respData, data, publicIP)
					#print "************NEW RESPONSE: ***************"
					#print response
					#print "******************************************"
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
				connSocket.sendto(respData, address)

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
		

		#convert a decimal integer to hex
		#decimal 12 will become "0c"
		#decimal 33 will become "21"
	def decimalToHexString(self, dec):
		print dec
		str = hex(dec).split('x')[-1]      
		if len(str) == 1:
			str = "0" + str
		return str        

	def createResponse(self, respData, data, publicIP):
		#import pdb; pdb.set_trace()
		#dataBits = self.hexToBits(data)
		identification = respData[:4]
		numQs = "\x00\x01"
		numAns = "\x00\x01"
		nAuth = "\x00\x00"
		nAdditional = "\x00\x00"

		flags = "\x81\x80"

		header = identification + flags + numQs + numAns + nAuth + nAdditional
		#import pdb; pdb.set_trace()
		#request header is 12 bytes -> 96 bits, so we just want the rest of it
		question = data[12:]

		myHostname = socket.gethostname()
		myAddr = socket.gethostbyname(myHostname)
		#dotlessAddr = myAddr.split(".")
		#myAddrHex = binascii.hexlify(socket.inet_aton('myAddr'))
		myAddrHex = "\x12\xbf\x1f\x7c"

		rLength = '\x00\x04'
		TTL = "\x00\x00\x00\x64"

		response = header + question + TTL + rLength + myAddrHex
		print "RESPONSE: ", response
		return response


if  __name__ =='__main__':  
	publicIP = "18.191.31.124"
	if len(sys.argv) > 1:
		publicIP = sys.argv[1]    
	print publicIP

	p = DNSProxy()
	p.dns_proxy(publicIP)
