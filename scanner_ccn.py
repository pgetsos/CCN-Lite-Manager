# -*- coding: utf-8 -*-
from logging import getLogger
from os import path, makedirs

import threading
import subprocess
import time

from parse import *

from config import *
from ext.sh import tail, killall, sudo, SignalException_SIGKILL, ErrorReturnCode_1, echo, rm

__license__ = """
	This file is part of Dedalus.

	Dedalus is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	Dedalus is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with Dedalus.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Petros Gketsopoulos'
__email__ = 'pgetsopoulos@hotmail.com'

_LOG = getLogger(__name__)
_DLOG = getLogger('dedalus_logger')

mn_sudo = sudo.bake("-S", _in=S_SUDO)

# CCN constants
REFRESH_TIME = 30


# TODO: add get paths and get neighbors functionality
# TODO: add documentation (we should review the documentation of all methods)
class CCNNode(object):
	def __init__(self):
		"""Init CCNNode instance.
		"""
		self.proto_info = {}
		self.proto_state = {'stats_info': {},
							'stats_bundles': {},
							'stats_conv': {},
							'neighbors': []}

	def info(self):
		# TODO what should we return ? what information do we need from ccn?
		return self.proto_state


class Scanner(object):
	def __init__(self):
		"""Init CCNScanner instance.
		"""
		self.node = CCNNode()
		self.formats = { # TODO Do I need this?
			'IBR-DTN': "IBR-DTN {proto_version} (build {build_num}) API {api_version}",
			'stats_info': "Uptime: {uptime}\nNeighbors: {neigh_num}\nStorage-size: {ssize}",
			'stats_bundles': "Stored: {storage}\nExpired: {expired}\nTransmitted: {transmitted}"
							 "\nAborted: {aborted}\nRequeued: {requeued}\nQueued: {queued}",
			'stats_conv': "TCP|in: {tcpin}\nTCP|out: {tcpout}"  #
		}

		self.process = None
		self.faces_ids = {}

		self.logs_path = path.abspath(path.join(path.dirname(__file__), '..', 'Log/CCN/'))
		#self.config_path = path.abspath(path.join(path.dirname(__file__), 'ibr.conf'))
		if not path.exists(self.logs_path):
			makedirs(self.logs_path)
		self.stop()
		self.start()

	def start(self):
		try:
			log_file = open(self.logs_path + '/ccn-start.log', "a")
			self.process = sudo("/home/pi/ccn-lite/build/bin/ccn-lite-relay", "-v", "trace", "-s", "ndn2013", "-u", "9998", "-x", "/tmp/mgmt-relay.sock", "-d", "/home/pi/ccn-lite/test/ndntlv", _out=log_file, _bg=True)
		except ErrorReturnCode_1:
			return 'a ccn instance was already running in this system'
	@staticmethod
	def stop():
		try:
			with mn_sudo:
				killall('ccn')
		except SignalException_SIGKILL:
			return 'ccn relay killed!'
		except ErrorReturnCode_1:
			return 'no running ccn instance found'

	@staticmethod
	def delete_sockets():
		try:
			with mn_sudo:
				rm('/tmp/mgmt-relay*')
				rm('/tmp/.ccn-light-ctrl-*') # Do we need seperate try-except for each rm ?
		except SignalException_SIGKILL:
			return 'ccn relay killed!'
		except ErrorReturnCode_1:
			return 'no running ccn instance found'

		return


	def get_routing_info(self):
		self._dump() # TODO add data to return
		return

	@staticmethod
	def get_current_interface():
		# TODO: get this dynamically
		return DEFAULT_INTEFACE

	def _dump(self):
		pass

	def get_node(self):
		"""Method that returns the ccn node.

		:rtype: CCNNode
		"""
		return self.node


	def search_content(self, local, path):
		log_search_file = open(self.logs_path + '/search.log', "a")
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-peek", "-s", "ndn2013", "-u", local+"/9998", path), "/home/pi/ccn-lite/build/bin/ccn-lite-pktdump", "-f", "2", _out=log_search_file,  _bg=True)
		return


	def create_content(self, filename, path, content):
		data_creation_file = open(self.logs_path + '/datacreation.txt', "a")
		echo(content, _out=data_creation_file)
		sudo("/home/pi/ccn-lite/build/bin/ccn-lite-mkC", "-s", "ndn2013", "-i", data_creation_file, "-o", "/home/pi/ccn-lite/test/ndntlv/" + filename + ".ndntlv", path, _bg=True)
		return

	# Read the RPi's IP address from the configuration file
	def get_local_address(self):
		local = "192.168.1.1"
		for line in tail("-n", "20", "-f", "/etc/network/interfaces", _iter=True):
			if "address 192.168.1." in line:
				local = line.split("address ")[1].splitlines()[0]
				break

		print("\nGot local address: " + local)
		return local


	# Read neighbors from IP Table using the route command and create faces for them via the specified address
	def get_neighbours_route(self):
		result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE)
		full = result.stdout.decode('utf-8')
		for line in full.splitlines():
			if "via" in line and line.startswith("192.168.1."):
				print(line)
				address = line.split(" ")[2].splitlines()[0]
				target = line.split(" ")[0].splitlines()[0]
				node = target.split("168.1.")[1]
				self.add_other_face(node, address)

	def neighbours_background(self):
		start_time = time.time()
		local_address = self.get_local_address()

		while True:
			self.add_face(local_address)
			print("Getting neighbors....")
			self.get_neighbours_route()

			time.sleep(REFRESH_TIME - ((time.time() - start_time) % REFRESH_TIME))

	# Reads the FACEID from the dump xml of CCN-Lite
	def read_face(self):
		face_dump_file = self.logs_path + '/facedump.log'
		with open(face_dump_file, encoding='utf-8', errors='ignore') as f:
			for line in f:
				if "FACEID" in line:
					node = line.split("FACEID>")[1].split("<")[0]
					for i in range(4):
						f.readline()
					line = f.readline()
					if "PEER" in line:
						return node

	# Create face based on address
	def add_face(self, address):
		node = address.split("168.1.")[1]
		sudo(sudo(sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "newUDPface", "any", address, "9998"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"), "grep", "FACEID"), "sed", "-e", "'s/^[^0-9]*\([0-9]\+\).*/\1/')")
		time.sleep(1)
		face_dump_file = open(self.logs_path + '/facedump.txt', "a")
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "debug", "dump"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml", _out=face_dump_file)
		time.sleep(1)
		face_id = self.read_face()
		if face_id is None:
			return
		self.delete_face(node)
		time.sleep(1)
		self.faces_ids[node] = face_id
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "prefixreg", "/node" + node, face_id, "ndn2013"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml")
		return


	# Create face of node via a different address
	def add_other_face(self, node, address):
		sudo(sudo(sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "newUDPface", "any", address, "9998"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml"), "grep", "FACEID"), "sed", "-e", "'s/^[^0-9]*\([0-9]\+\).*/\1/')")
		time.sleep(1)
		face_dump_file = open(self.logs_path + '/facedump.txt', "a")
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "debug", "dump"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml", _out=face_dump_file)
		time.sleep(1)
		face_id = self.read_face()
		if face_id is None:
			return
		self.delete_face(node)
		time.sleep(1)
		self.faces_ids[node] = face_id
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "prefixreg", "/node" + node, face_id, "ndn2013"), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml")
		return


	# Delete a face of a node -NOT address
	def delete_face(self, node):
		if node in self.faces_ids:
			face_to_delete = self.faces_ids[node]
		else:
			return
		sudo(sudo("/home/pi/ccn-lite/build/bin/ccn-lite-ctrl", "-x", "/tmp/mgmt-relay.sock", "destroyface", face_to_delete), "/home/pi/ccn-lite/build/bin/ccn-lite-ccnb2xml")
		return

if __name__ == "__main__":
	pass
