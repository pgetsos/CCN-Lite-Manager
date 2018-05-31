#!/usr/bin/python3.5

from test_helpers import create_content_auto, search_content_auto
from ccn_management import openrelay, close_relay, add_face
from readers import get_local_address, get_neighbours_route
import time


def run_auto_41():
	create_content_auto(6)
	create_content_auto(7)
	create_content_auto(8)
	create_content_auto(9)
	create_content_auto(10)
	time.sleep(2)
	openrelay()


def run_auto_42():
	local_address = get_local_address()

	openrelay()
	time.sleep(2)

	start_time = time.time()

	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()


		time.sleep(20.0 - ((time.time() - start_time) % 20.0))


def run_auto_43():
	local_address = get_local_address()

	openrelay()
	time.sleep(2)

	start_time = time.time()

	counter = 1
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()

		time.sleep(1)

		search_content_auto(local_address, 6, "4.1-"+str(counter))
		search_content_auto(local_address, 7, "4.2-"+str(counter))
		search_content_auto(local_address, 8, "4.3-"+str(counter))
		search_content_auto(local_address, 9, "4.4-"+str(counter))
		search_content_auto(local_address, 10, "4.5-"+str(counter))

		time.sleep(2)

		search_content_auto(local_address,  6, "4.6-"+str(counter))
		search_content_auto(local_address,  7, "4.7-"+str(counter))
		search_content_auto(local_address,  8, "4.8-"+str(counter))
		search_content_auto(local_address,  9, "4.9-"+str(counter))
		search_content_auto(local_address, 10, "4.10-"+str(counter))

		time.sleep(5)

		close_relay()
		time.sleep(2)

		openrelay()
		time.sleep(1)
		get_neighbours_route()
		time.sleep(1)

		search_content_auto(local_address,  6, "4.11-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  7, "4.12-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  8, "4.13-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  9, "4.14-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address, 10, "4.15-"+str(counter))
		time.sleep(1)
		counter = counter + 1
		if counter == 4:
			break
		time.sleep(20.0 - ((time.time() - start_time) % 20.0))
	print("FINISHED!")
