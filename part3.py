import socket
import sys

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamAddr = ('8.8.8.8', 53)
		self.sockUDP = None
		self.upstreamSockUDP = None
		self.sockTCP = None
		self.upstreamSockTCP = None

	def dns_proxy(self):
		self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockUDP.bind(("0.0.0.0", self.port))
		self.upstreamSockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.upstreamSockUDP.connect(self.upstreamAddr)

		self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockTCP.bind(("0.0.0.0", self.port))
		self.sockTCP.listen(1)
		self.upstreamSockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.upstreamSockTCP.connect(self.upstreamAddr)
		#self.upstreamSockTCP.listen(1)


		while True:
			print "waiting to receive message"

			#try udp
			data, address = self.sockUDP.recvfrom(4096)
			if data:
				print "processing UDP"
				self.UDP(data, address)


			#try tcp
			connSocket, address = self.sockTCP.accept()
			data, address = connSocket.recvfrom(4096)
			if data:
				print "processing TCP"
				self.TCP(data, address)

	def UDP(self, data, address):
		print "received ", len(data), " bytes from ", address
		print "addr: ", address, " data length: ", len(data)
		
		self.upstreamSockUDP.send(data)
		print "wait for a response from upstream"
		respData, respAddr = self.upstreamSockUDP.recvfrom(4096)
		print "we got our response data, response length: ", len(respData)
		if respData:
			print "sending data back"
			sent = self.sockUDP.sendto(respData, address)

	def TCP(self, data, address):
		print "received ", len(data), " bytes from ", address
		print "addr: ", address, " data length: ", len(data)

		self.upstreamSockTCP.send(data)
		upstreamConnSock, address = self.upstreamSockTCP.accept()
		respData, respAddr = upstreamConnSock.recvfrom(4096)
		#print "we got our response data, response length: ", len(respData)
		if respData:
			print "sending response data back"
			self.sockTCP.sendto(respData, address)





if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
