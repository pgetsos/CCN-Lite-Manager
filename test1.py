#!/usr/bin/python3.5

from test_helpers import create_content_auto, search_content_auto
from ccn_management import open_relay, close_relay, add_face
from readers import get_local_address
from ccn_config import SERVER_NODE
import time


def run_auto_11():
	create_content_auto(1)
	create_content_auto(2)
	create_content_auto(3)
	create_content_auto(4)
	create_content_auto(5)
	time.sleep(3)
	open_relay()


def run_auto_12():
	local_address = get_local_address()

	open_relay()
	time.sleep(3)
	add_face("192.168.1."+str(SERVER_NODE))
	search_content_auto(local_address, 1, "1.1")
	search_content_auto(local_address, 2, "1.2")
	search_content_auto(local_address, 3, "1.3")
	search_content_auto(local_address, 4, "1.4")
	search_content_auto(local_address, 5, "1.5")

	time.sleep(10)

	search_content_auto(local_address, 1, "1.6")
	search_content_auto(local_address, 2, "1.7")
	search_content_auto(local_address, 3, "1.8")
	search_content_auto(local_address, 4, "1.9")
	search_content_auto(local_address, 5, "1.10")

	time.sleep(10)

	close_relay()
	time.sleep(5)

	open_relay()
	time.sleep(5)
	add_face("192.168.1."+str(SERVER_NODE))
	time.sleep(5)
	search_content_auto(local_address, 1, "1.11")
	time.sleep(3)
	search_content_auto(local_address, 2, "1.12")
	time.sleep(3)
	search_content_auto(local_address, 3, "1.13")
	time.sleep(3)
	search_content_auto(local_address, 4, "1.14")
	time.sleep(3)
	search_content_auto(local_address, 5, "1.15")
	time.sleep(3)
	search_content_auto(local_address, 1, "1.16")
	time.sleep(3)
	search_content_auto(local_address, 2, "1.17")
	time.sleep(3)
	search_content_auto(local_address, 3, "1.18")
	time.sleep(3)
	search_content_auto(local_address, 4, "1.19")
	time.sleep(3)
	search_content_auto(local_address, 5, "1.20")
	time.sleep(3)
	print("FINISHED")
