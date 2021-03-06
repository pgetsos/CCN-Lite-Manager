#!/usr/bin/python3.5

from test_helpers import create_content_auto, search_content_auto
from ccn_management import open_relay, close_relay, add_face
from readers import get_local_address, get_neighbours_route
from ccn_config import REFRESH_TIME
import time


def run_auto_21():
	create_content_auto(6)
	create_content_auto(7)
	create_content_auto(8)
	create_content_auto(9)
	create_content_auto(10)
	time.sleep(2)
	open_relay()


def run_auto_22():
	local_address = get_local_address()

	open_relay()
	time.sleep(2)

	start_time = time.time()

	counter = 1
	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()

		time.sleep(1)

		search_content_auto(local_address, 6, "2.1-"+str(counter))
		search_content_auto(local_address, 7, "2.2-"+str(counter))
		search_content_auto(local_address, 8, "2.3-"+str(counter))
		search_content_auto(local_address, 9, "2.4-"+str(counter))
		search_content_auto(local_address, 10, "2.5-"+str(counter))

		time.sleep(2)

		search_content_auto(local_address,  6, "2.6-"+str(counter))
		search_content_auto(local_address,  7, "2.7-"+str(counter))
		search_content_auto(local_address,  8, "2.8-"+str(counter))
		search_content_auto(local_address,  9, "2.9-"+str(counter))
		search_content_auto(local_address, 10, "2.10-"+str(counter))

		time.sleep(5)

		close_relay()
		time.sleep(2)

		open_relay()
		time.sleep(1)
		get_neighbours_route()
		time.sleep(1)

		search_content_auto(local_address,  6, "2.11-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  7, "2.12-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  8, "2.13-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address,  9, "2.14-"+str(counter))
		time.sleep(1)
		search_content_auto(local_address, 10, "2.15-"+str(counter))
		time.sleep(1)
		counter = counter + 1
		if counter == 4:
			break
		time.sleep(REFRESH_TIME - ((time.time() - start_time) % REFRESH_TIME))
	print("FINISHED!")
