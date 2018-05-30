#!/usr/bin/python3.5

from test_helpers import create_content_auto, search_content_auto
from ccn_management import openrelay, close_relay, add_face
from readers import get_local_address, get_neighbours_route
import time


def run_auto_21():
	create_content_auto(6)
	create_content_auto(7)
	create_content_auto(8)
	create_content_auto(9)
	create_content_auto(10)
	time.sleep(3)
	openrelay()


def run_auto_22():
	local_address = get_local_address()

	openrelay()
	time.sleep(3)

	start_time = time.time()

	counter = 1
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()

		time.sleep(3)

		search_content_auto(local_address, 6, "2.1-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address, 7, "2.2-"+str(counter))
		search_content_auto(local_address, 8, "2.3-"+str(counter))
		search_content_auto(local_address, 9, "2.4-"+str(counter))
		search_content_auto(local_address, 10, "2.5-"+str(counter))

		time.sleep(3)

		search_content_auto(local_address,  6, "2.6-"+str(counter))
		search_content_auto(local_address,  7, "2.7-"+str(counter))
		search_content_auto(local_address,  8, "2.8-"+str(counter))
		search_content_auto(local_address,  9, "2.9-"+str(counter))
		search_content_auto(local_address, 10, "2.10-"+str(counter))

		time.sleep(3)

		close_relay()
		time.sleep(5)

		openrelay()
		time.sleep(3)
		get_neighbours_route()
		time.sleep(3)

		search_content_auto(local_address,  6, "2.11-"+counter)
		time.sleep(1)
		search_content_auto(local_address,  7, "2.12-"+counter)
		time.sleep(1)
		search_content_auto(local_address,  8, "2.13-"+counter)
		time.sleep(1)
		search_content_auto(local_address,  9, "2.14-"+counter)
		time.sleep(1)
		search_content_auto(local_address, 10, "2.15-"+counter)
		time.sleep(1)
		counter = counter + 1
		if counter == 6:
			break
		time.sleep(30.0 - ((time.time() - start_time) % 30.0))
	print("FINISHED!")
