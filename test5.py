#!/usr/bin/python3.5

from test_helpers import create_content_auto_with_node, create_content, search_content
from ccn_management import open_relay, add_face, restart_relay
from readers import get_local_address, get_neighbours_route
from ccn_config import REFRESH_TIME
import time
import threading


def run_auto_51(auto_create):
	local_address = get_local_address()
	time.sleep(1)

	local_node = local_address.split("168.1.")[1]

	if auto_create == 1:
		auto_create_content(local_node)

	time.sleep(2)

	open_relay()

	time.sleep(2)

	download_thread = threading.Thread(target=neighbours_background)
	download_thread.start()

	while True:
		ccn_choice = input("Choose action: \n1. Search for content\n2. Create content\n 3. Continue")
		if ccn_choice == '1':
			search_content(local_address)
		elif ccn_choice == '2':
			create_content(local_node)
			restart_relay()  # Restart relay to see new content
			neighbour_search()
		elif ccn_choice == '3':
			break
		else:
			print("\n!!! This choice doesn't exist, please try again !!!\n")


def neighbours_background():
	start_time = time.time()
	local_address = get_local_address()

	while True:
		add_face(local_address)
		print("Getting neighbors....")
		get_neighbours_route()

		time.sleep(REFRESH_TIME - ((time.time() - start_time) % REFRESH_TIME))


def neighbour_search():
	local_address = get_local_address()
	add_face(local_address)
	get_neighbours_route()


def auto_create_content(local_node):
	create_content_auto_with_node(1, local_node)
	create_content_auto_with_node(2, local_node)
	create_content_auto_with_node(3, local_node)
	create_content_auto_with_node(4, local_node)
	create_content_auto_with_node(5, local_node)
	create_content_auto_with_node(6, local_node)
	create_content_auto_with_node(7, local_node)
	create_content_auto_with_node(8, local_node)
	create_content_auto_with_node(9, local_node)
	create_content_auto_with_node(10, local_node)
