import socket
import sys

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamAddr = ('8.8.8.8', 8000)

	def dns_proxy(self):
		print "starting dns proxy"
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			sock.bind(("0.0.0.0", self.port))
			print "socket created."
		except:
			print "socket failed to be created. error: ", socket.error

		upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			upstreamSock.connect(self.upstreamAddr)
			print "upstreamSock connected."
		except:
			print "upstreamSock could not connect. error: ", socket.error

		while True:
			print "waiting to receive message"
			data, address = sock.recvfrom(4096)
			print "received ", len(data), " bytes from ", address
			if not data:
				print "failed to get data"
				break
			#we got something! so we want to send it to the upstream DNS resolver
			print "addr: ", address, " data length: ", len(data)
			print "we got something"
			sent = upstreamSock.send(data)
			#wait for a response
			respData, respAddr = upstreamSock.recvfrom(4096)
			if respData:
				sent = upstreamSock.sendto(respData, address)


if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
