#!/usr/bin/python3.5

import subprocess
import time
from readers import read_face

faces_ids = {}


# Open a relay for ccn-lite in the background
def open_relay():
	delete_sockets()
	print("Opening relay...")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-relay -v trace -s ndn2013 -u 9998 -x /tmp/mgmt-relay.sock -d /home/pi/ccn-lite/test/ndntlv > /home/pi/ccn.log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Close a relay for ccn-lite
def close_relay():
	delete_sockets()
	print("Closing relay...")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock debug halt | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml > /home/pi/ccn-closing.log 2>&1 &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Automatically restart relay
def restart_relay():
	time.sleep(1)
	close_relay()
	time.sleep(1)
	open_relay()


# Delete the old sockets
def delete_sockets():
	print("Deleting temporary sockets...")
	bash_command = "rm /tmp/mgmt-relay* &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	bash_command = "rm /tmp/.ccn-light-ctrl-* &"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create face based on address
def add_face(address):
	print("Adding face for: "+address)
	node = address.split("168.1.")[1]
	bash_command = "FACEID=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(1)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock debug dump | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml > /home/pi/face_dump.log 2>&1"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(1)
	face_id = read_face()
	if face_id is None:
		return
	delete_face(node)
	time.sleep(1)
	faces_ids[node] = face_id
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock prefixreg /node" + node + " " + face_id + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Create face of node via a different address
def add_other_face(node, address):
	print("Adding neighbor: " + node)
	bash_command = "FACEID=$(/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock newUDPface any " + address + " 9998 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/')"
	print("Adding forwarding rule through: " + address)
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(1)
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock debug dump | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml > /home/pi/face_dump.log 2>&1"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	time.sleep(1)
	face_id = read_face()
	if face_id is None:
		return
	delete_face(node)
	time.sleep(1)
	faces_ids[node] = face_id
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock prefixreg /node" + node + " " + face_id + " ndn2013 | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	print("Added neighbor: " + node + " through: " + address)
	return


# Delete a face of a node -NOT address
def delete_face(node):
	if node in faces_ids:
		face_to_delete = faces_ids[node]
	else:
		return
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-ctrl -x /tmp/mgmt-relay.sock destroyface " + face_to_delete + " | /home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return
