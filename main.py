#!/usr/bin/python3.5

import subprocess
import sh
from faces import faces_array
import time

neighbors = []


# Open a relay for ccn-lite in the background
def openrelay():
	bash_command = "~/ccn-lite/build/bin/ccn-lite-relay -v trace -s ndn2013 -u 9998 -x /tmp/mgmt-relay-a.sock &"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
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
			print("Adding neighbor: " + node + " through: " + address)
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
	bash_command = "FACEID" + node + "=$(~/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock newUDPface any " + address + " 9998 | ~/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID" + node + " | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
	bash_command = "~/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock prefixreg /node" + node + " $FACEID" + node + " ndn2013 | ~/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
	return


# Create face of node via a different address
def add_other_face(node, address):
	bash_command = "FACEID" + node + "=$(~/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock newUDPface any " + address + " 9998 | ~/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID" + node + " | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
	bash_command = "~/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock prefixreg /node" + node + " $FACEID" + node + " ndn2013 | ~/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
	return


# Delete a face of a node -NOT address
def delete_face(address):
	node = address.split("168.1.")[1]
	bash_command = "$CCNL_HOME/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay-a.sock destroyface $FACEID" + node + " | $CCNL_HOME/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE, shell=True)
	return


openrelay()
local_address = get_local_address()
starttime = time.time()
while True:
	print("Getting neighbors....")
	get_neighbours_route()
	time.sleep(30.0 - ((time.time() - starttime) % 30.0))
