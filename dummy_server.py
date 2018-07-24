import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 6666)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

while True:
	print('\nwaiting to receive message')
	data, address = sock.recvfrom(4096)

	print('received %s bytes from %s' % (len(data), address))
	print(data)
	data_string = str(data)
	data_string = data_string.split("node")[1]
	data_string = data_string.split("\\")[0]

	print("Node: "+data_string)

	if data:
		time.sleep(30)
		sent = sock.sendto(data, address)
		print('sent %s bytes back to %s' % (sent, address))
