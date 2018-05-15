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
			while True:
				respData, respAddr = upstreamSockTCP.recvfrom(4096)
				connSocket.sendto(respData, address)
				if len(respData) < 4096:
					break

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
		#convert incoming response from string to hex
		#so if a byte in string is "21", we will get 33 integer value
		hexRespData = []
		for i in range(0, len(respData)):
			hexRespData.append(binascii.hexlify(respData[i]))
		newheader = []
		#copy identification field from old header
		for i in range(0, 12):
			newheader.append(hexRespData[i])
		        
		#change the response code to 0000
		flag = "00"
		newheader[2] = flag
		newheader[3] = flag

		#update the answer field to contain 1 answer
		newheader[6] = "00"
		newheader[7] = "01"

		#next section is question section
		#query name section ends with "00", followed by query type and class
		index = 12  #start after header
		queryName = ""
		#question section should be the same as the old response we received
		#"00" indicates the end
		while True:
			if hexRespData[index] != "00":
				queryName += hexRespData[index]
			else:
				break
			index = index + 1
		                
		queryName += "00"   #add "00" ourselves

		#class type 2 bytes, same as old response
		queryType = "0001"

		#query class 2 bytes, same as old response
		queryClass = "0001"

		#time to live, 4 bytes, just set to some value
		ttl = "00000064"   

		#data length, 2 bytes
		dataLength = "0004"   #ip 4 address  xxx.xxx.xxx.xxx will take 4 bytes

		#put my host ip as answer
		dotlessAddr = publicIP.split(".")
		print "dotlessAddr: ", dotlessAddr
		address = []
		for i in range(0, len(dotlessAddr)):
			thisPart = dotlessAddr[i]       
			address.append(self.decimalToHexString(int(thisPart)))
		querySection = queryName + queryType + queryClass
		answerSection = "c00c" + "".join(queryType) + "".join(queryClass) + ttl + dataLength + "".join(address)
		        
		strResponse = "".join(newheader) + querySection + answerSection
		return strResponse.decode('hex')


if  __name__ =='__main__':  
	publicIP = "18.191.31.124"
	if len(sys.argv) > 1:
		publicIP = sys.argv[1]    
	print publicIP

	p = DNSProxy()
	p.dns_proxy(publicIP)
