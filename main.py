#!/usr/bin/python3.5 -u

import subprocess
import sh
from faces import faces_array
import time

import zmq
import msgpack
from zmq.eventloop.ioloop import IOLoop
from client_runner import ClientRunner
from config import MSG_DUMP, CLIENT_PROTO, SERVICE_ECHO
from logging import getLogger

_LOG = getLogger(__name__)
neighbors = []


# Create content for ccn-lite
def create_content(node):
	path = input("Local path (don't include initial '/'): ")
	name = input("File name: ")
	content = input("Content: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 /node" + node + "/" + path + " > /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv << "+content
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create content for ccn-lite
def search_content(local):
	path = input("Lookup path: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Open a relay for ccn-lite in the background
def openrelay():
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-relay -v trace -s ndn2013 -u 9998 -x /tmp/mgmt-relay-a.sock -d /home/pi/ccn-lite/test/ndntlv > /home/pi/ccn.log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Read the RPi's IP address from the configuration file
def get_local_address():
	local = "192.168.1.1"
	for line in sh.tail("-f", "/etc/network/interfaces", _iter=True):
		if "address 192.168.1." in line:
			local = line.split("address ")[1].splitlines()[0]
			break

	print("\nGot local address: " + local)
	return local


# Read neighbors from babel - not in use
def get_neighbours(local):
	for line in sh.tail("-f", "/home/pi/babeld.log", _iter=True):
		if line.startswith("192.168.1.") and "nexthop " in line and local not in line:
			target = line.split("/")[0].splitlines()[0]
			node = target.split("168.1.")[1]
			address = line.split("nexthop ")[1].split(" ")[0]
			add_other_face(node, address)


# Read neighbors from IP Table and create faces for them
def get_neighbours_table():
	result = subprocess.run(['ip', 'neighbor'], stdout=subprocess.PIPE)
	old_neighbors = neighbors
	neighbors.clear()
	full = result.stdout.decode('utf-8')
	for line in full.splitlines():
		print(line)
		if "192.168.1." in line and line.startswith("192"):
			neighbors.append(line.split(" ")[0].splitlines()[0])
	for old in old_neighbors:
		if old not in neighbors:
			delete_face(old)
	for neighbor in neighbors:
		print("Adding neighbor: " + neighbor)
		add_face(neighbor)


# Read neighbors from IP Table using the route command and create faces for them via the specified address
def get_neighbours_route():
	result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE)
	old_neighbors = neighbors
	neighbors.clear()
	full = result.stdout.decode('utf-8')
	for line in full.splitlines():
		if "via" in line and line.startswith("192.168.1."):
			print(line)
			address = line.split(" ")[2].splitlines()[0]
			target = line.split(" ")[0].splitlines()[0]
			node = target.split("168.1.")[1]
			neighbors.append(target)
			add_other_face(node, address)
	for old in old_neighbors:
		if old not in neighbors:
			delete_face(old)


# Send unknown hosts to first neighbor
def add_rest():
	for face in faces_array:
		if face.ip not in neighbors:
			add_other_face(face.nodenum, neighbors[0])


# Create face based on address
def add_face(address):
	node = address.split("168.1.")[1]
	bash_command = "FACEID" + node + "=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID" + node + " | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock prefixreg /node" + node + " $FACEID" + node + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create face of node via a different address
def add_other_face(node, address):
	print("Adding neighbor: " + node)
	bash_command = "FACEID" + node + "=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID" + node + " | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	print("Adding forwarding rule through: " + address)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock prefixreg /node" + node + " $FACEID" + node + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	print("Added neighbor: " + node + " through: " + address)
	return


# Delete a face of a node -NOT address
def delete_face(address):
	node = address.split("168.1.")[1]
	bash_command = "$CCNL_HOME/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock destroyface $FACEID" + node + " | $CCNL_HOME/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	print("Deleted face to: " + address)
	return


if __name__ == "__main__":
	local_address = get_local_address()

	while True:
		ccn_choice = input("Choose action: \n1. Create content\n2. Open CCN server\n3. Search for content (requires an open server!)")
		if ccn_choice == '1':
			create_content(local_address.split("168.1.")[1])
		elif ccn_choice == '2':
			break
		elif ccn_choice == '3':
			search_content(local_address)
		else:
			print("\n!!! This choice doesn't exist, please try again !!!\n")

	openrelay()
	starttime = time.time()
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()

		addressD = "tcp://192.168.1.1:5555"
		context = zmq.Context()
		client = ClientRunner(context, addressD, SERVICE_ECHO)
		print("Running IOLoop")
		try:
			IOLoop.instance().start()
			print("Finished...")
			client.shutdown()
		except KeyboardInterrupt:
			_LOG.info("Interrupt received, stopping!")
		finally:
			# clean up
			client.shutdown()
			context.term()

		time.sleep(30.0 - ((time.time() - starttime) % 30.0))
