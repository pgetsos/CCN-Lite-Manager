#!/usr/bin/python3.5

from test_helpers import create_content_auto, search_content_auto
from ccn_management import open_relay, add_face
from readers import get_local_address
import time


def run_auto_31():
	create_content_auto(11)
	time.sleep(3)
	open_relay()


def run_auto_32():
	local_address = get_local_address()

	open_relay()
	time.sleep(3)

	counter = 1
	while True:
		add_face("192.168.1.1")
		time.sleep(1)

		search_content_auto(local_address, 11, "3.1-"+str(counter))

		counter = counter + 1
		if counter == 31:
			break
	print("FINISHED!")
