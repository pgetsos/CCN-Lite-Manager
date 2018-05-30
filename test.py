#!/usr/bin/python3.5

import subprocess
import time
import sys
from ccn_management import add_face, openrelay
from readers import get_local_address, get_neighbours_route
from test1 import run_auto_11, run_auto_12
from test2 import run_auto_21, run_auto_22


neighbors = []
faces_ids = {}


# Create content for ccn-lite
def create_content(node):
	path = input("Local path (don't include initial '/'): ")
	name = input("File name: ")
	content = input("Content: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-mkC -s ndn2013 /node" + node + "/" + path + " > /home/pi/ccn-lite/test/ndntlv/" + name + ".ndntlv << "+content
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


# Search content for ccn-lite
def search_content(local):
	path = input("Lookup path: ")
	bash_command = "/home/pi/ccn-lite/build/bin/ccn-lite-peek -s ndn2013 -u " + local + "/9998 " + path + " | /home/pi/ccn-lite/build/bin/ccn-lite-pktdump -f 2 "
	subprocess.Popen(bash_command, stdout=subprocess.PIPE, shell=True)
	return


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
		if sys.argv[1] == "test":
			if sys.argv[1] == "11":
				run_auto_11()
			elif sys.argv[1] == "12":
				run_auto_12()
			elif sys.argv[1] == "21":
				run_auto_21()
			elif sys.argv[1] == "22":
				run_auto_22()
