#!/usr/bin/python3.5

import subprocess
import sh
from faces import faces_array
import time
from xml.dom import minidom
import sys

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


# Create automatically content for ccn-lite
def create_content_auto(num):
	path = "text/text"+num
	name = "text"+num
	content = "This is the content from text: "+num
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 /node" + str(1) + "/" + path + " > /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv << "+content
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search content for ccn-lite
def search_content(local):
	path = input("Lookup path: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search automatically content for ccn-lite
def search_content_auto(num):
	path = "/node1/text/text"+num
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Open a relay for ccn-lite in the background
def openrelay():
	delete_sockets()
	print("Opening relay...")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-relay -v trace -s ndn2013 -u 9998 -x /tmp/mgmt-relay.sock -d /home/pi/ccn-lite/test/ndntlv > /home/pi/ccn.log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Delete the old sockets
def delete_sockets():
	print("Deleting temporary sockets...")
	bash_command = "rm /tmp/mgmt-relay*"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	bash_command = "rm /tmp/.ccn-light-ctrl-*"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Read the RPi's IP address from the configuration file
def get_local_address():
	local = "192.168.1.1"
	for line in sh.tail("-n", "20", "-f", "/etc/network/interfaces", _iter=True):
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
def add_face2(address):
	delete_face(address)
	print("Adding face for: "+address)
	node = address.split("168.1.")[1]
	bash_command = "FACEID" + node + "=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock prefixreg /node" + node + " $FACEID" + node + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	command = "echo $FACEID" + node + " > /home/pi/lol.log 2>&1 &"
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return


# Create face based on address
def add_face(address):
	# delete_face(address)
	print("Adding face for: "+address)
	node = address.split("168.1.")[1]
	bash_command = "FACEID=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(1)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock debug dump | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml > /home/pi/face_dump.log 2>&1"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(3)
	face_id = read_face()
	print(node)
	print(face_id)
	if face_id is None:
		return
	# value, err = p.communicate()
	# face_num = ord(value.split()[0])
	# print(face_num)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock prefixreg /node" + node + " " + face_id + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	# command = "echo " + str(face_num) + " > /home/pi/lol.log 2>&1 &"
	# subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	return


# Create face of node via a different address
def add_other_face(node, address):
	print("Adding neighbor: " + node)
	bash_command = "FACEID=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	print("Adding forwarding rule through: " + address)
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(3)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock debug dump | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml > /home/pi/face_dump.log 2>&1"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(3)
	face_id = read_face()
	print(node)
	print(face_id)
	if face_id is None:
		return
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock prefixreg /node" + node + " " + face_id + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	print("Added neighbor: " + node + " through: " + address)
	return


# Delete a face of a node -NOT address
def delete_face(address):
	print("Deleting face to: " + address)
	node = address.split("168.1.")[1]
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock destroyface $FACEID" + node + " | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


def read_face():
	with open('/home/pi/face_dump.log', encoding='utf-8', errors='ignore') as f:
		for line in f:
			if "FACEID" in line:
				node = line.split("FACEID>")[1].split("<")[0]
				for i in range(4):
					f.readline()
				line = f.readline()
				if "PEER" in line:
					return node


def run_auto_11():
	create_content_auto(1)
	create_content_auto(2)
	create_content_auto(3)
	create_content_auto(4)
	create_content_auto(5)
	time.sleep(3)
	openrelay()


def run_auto_12():
	openrelay()
	add_face("192.168.1.1")


def run_without_args():
	local_address = get_local_address()
	openrelay()
	start_time = time.time()
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()
		time.sleep(30.0 - ((time.time() - start_time) % 30.0))


def run_with_args():
	local_address = get_local_address()
	while True:
		ccn_choice = input(
			"Choose action: \n1. Create content\n2. Open CCN server\n3. Search for content (requires an open server!)\n4. Continue")
		if ccn_choice == '1':
			create_content(local_address.split("168.1.")[1])
		elif ccn_choice == '2':
			openrelay()
		elif ccn_choice == '3':
			search_content(local_address)
		elif ccn_choice == '4':
			break
		else:
			print("\n!!! This choice doesn't exist, please try again !!!\n")
	local_address = get_local_address()
	openrelay()
	start_time = time.time()
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()
		time.sleep(30.0 - ((time.time() - start_time) % 30.0))


if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] == "auto":
			if sys.argv[1] == "11":
				run_auto_11()
		else:
			run_with_args()
	else:
		run_without_args()

		# addressD = "tcp://192.168.1.1:5555"
		# context = zmq.Context()
		# client = ClientRunner(context, addressD, SERVICE_ECHO)
		# print("Running IOLoop")
		# io_loop = IOLoop.instance()
		# try:
		# 	io_loop.start()
		# 	print("Finished...")
		# 	client.shutdown()
		# except KeyboardInterrupt:
		# 	_LOG.info("Interrupt received, stopping!")
		# except Exception as e:
		# 	Log.error("Hmm...", e)
		# finally:
		# 	# clean up
		# 	client.shutdown()
		# 	context.term()
		# 	io_loop.stop()
