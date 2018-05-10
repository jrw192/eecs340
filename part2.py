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
			sock.bind(("", self.port))
			print("socket created.")
		except:
			print "socket failed to be created. error: ", socket.error

		upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			upstreamSock.connect(self.upstreamAddr)
		except:
			print "upstreamSock could not connect. error: ", socket.error

		while True:
			data, addr = sock.recvfrom(4096)
			if not datagram:
				print "failed to get data"
				break
			#we got something! so we want to send it to the upstream DNS resolver
			print "we got something"
			sent = upstreamSock.send(data)
			#wait for a response
			respData, respAddr = upstreamSock.recvfrom(4096)
			if respData:
				sent = sock.send(respData)
				sentBack = sock.sendto(respData, addr)


if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
