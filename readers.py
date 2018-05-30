#!/usr/bin/python3.5

import subprocess
import sh


# Read the RPi's IP address from the configuration file
def get_local_address():
	local = "192.168.1.1"
	for line in sh.tail("-n", "20", "-f", "/etc/network/interfaces", _iter=True):
		if "address 192.168.1." in line:
			local = line.split("address ")[1].splitlines()[0]
			break

	print("\nGot local address: " + local)
	return local


# Read neighbors from IP Table using the route command and create faces for them via the specified address
def get_neighbours_route():
	from ccn_management import add_other_face
	result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE)
	full = result.stdout.decode('utf-8')
	for line in full.splitlines():
		if "via" in line and line.startswith("192.168.1."):
			print(line)
			address = line.split(" ")[2].splitlines()[0]
			target = line.split(" ")[0].splitlines()[0]
			node = target.split("168.1.")[1]
			add_other_face(node, address)


# Reads the FACEID from the dump xml of CCN-Lite
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
