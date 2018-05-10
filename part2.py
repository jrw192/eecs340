import socket
import sys

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamDest = 8.8.8.8

	def dns_proxy(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(("", self.port))

		upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		upstreamSock.connect(self.upstreamDest)

		while True:
			datagram = sock.recv(4096)

			if datagram:
				#we got something! so we want to send it to the upstream DNS resolver
				sent = upstreamSock.send(datagram)
				#wait for a response
				response = upstreamSock.recv(4096)

				if response:
					sent = sock.send(response)




if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()