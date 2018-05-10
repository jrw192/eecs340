import socket
import sys

class DNSProxy:
	def __init__(self):
		self.port = 53
		self.upstreamAddr = ('8.8.8.8', 53)

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
			print "sent: ", sent
                        print "wait for a response from upstream"
			respData, respAddr = upstreamSock.recvfrom(4096)
                        print "we got our response data, response length: ", len(respData)
			if respData:
                                print "sending data back"
                                sent = sock.sendto(respData, address)
				#sent = upstreamSock.sendto(respData, address)


if  __name__ =='__main__':  
	p = DNSProxy()
	p.dns_proxy()
