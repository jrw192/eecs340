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
		self.upstreamSockTCP.listen(1)


		while True:
			print "waiting to receive message"
			data, address = self.sockUDP.recvfrom(4096)

			if not data:
				#probably TCP then
				print "processing TCP"
				connSocket, address = self.sockTCP.accept()
				data, address = connSocket.recvfrom(4096)
				if data:
					TCP(self, data, address)
				if not data:
					print "bad request"
					break
			elif data:
				print "processing TCP"
				UDP(self, data, address)


	def UDP(self, data, address):
		print "received ", len(data), " bytes from ", address
		print "addr: ", address, " data length: ", len(data)
		
		sent = self.upstreamSockUDP.send(data)
		print "sent: ", sent
		print "wait for a response from upstream"
		respData, respAddr = self.upstreamSockUDP.recvfrom(4096)
		print "we got our response data, response length: ", len(respData)
		if respData:
			print "sending data back"
			sent = self.sockUDP.sendto(respData, address)

	def TCP(self, data, address)
		print "received ", len(data), " bytes from ", address
		print "addr: ", address, " data length: ", len(data)

		

if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
