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
					print "--------DONE--------"
				elif s is sockTCP:
					print "using tcp to listen"
					self.TCP(s)
					print "--------DONE--------"


	def UDP(self, sockUDP):
		data, address = sockUDP.recvfrom(4096)
		if data:
			print "UDP received ", len(data), " bytes from ", address
			#print "addr: ", address, " data length: ", len(data)
			
			upstreamSockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			upstreamSockUDP.connect(self.upstreamAddr)

			upstreamSockUDP.send(data)
			print "wait for a response from upstream"
			respData, respAddr = upstreamSockUDP.recvfrom(4096)
			print "UDP we got our response data, response length: ", len(respData)
			if respData:
				print "sending data back"
				sent = sockUDP.sendto(respData, address)
			upstreamSockUDP.close()

	def TCP(self, sockTCP):

		connSocket, address = sockTCP.accept()
		data, __ = connSocket.recvfrom(4096)
		if data:
			print "TCP received ", len(data), " bytes from ", address

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




if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()