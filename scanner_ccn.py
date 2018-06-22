# -*- coding: utf-8 -*-
from logging import getLogger
from os import path, makedirs

from parse import *

from config import *
from ext.sh import killall, sudo, SignalException_SIGKILL, ErrorReturnCode_1, echo, rm

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
IBR_RECEIVER = 'receiver'  # names
IBR_SENDER = 'sender'


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
	def __init__(self, ip='::1', port=4550, buffer_size=1024):
		"""Init CCNScanner instance.
		"""
		self.ip = ip
		self.port = port
		self.buffer_size = buffer_size
		self.socket = None
		self.fsock = None
		self.protocol = 'epidemic'  # TODO: get this dynamically

		self.node = CCNNode()
		self.formats = {
			'IBR-DTN': "IBR-DTN {proto_version} (build {build_num}) API {api_version}",
			'stats_info': "Uptime: {uptime}\nNeighbors: {neigh_num}\nStorage-size: {ssize}",
			'stats_bundles': "Stored: {storage}\nExpired: {expired}\nTransmitted: {transmitted}"
							 "\nAborted: {aborted}\nRequeued: {requeued}\nQueued: {queued}",
			'stats_conv': "TCP|in: {tcpin}\nTCP|out: {tcpout}"  #
		}
		self.status_codes = {
			'API_STATUS_CONTINUE': 100,
			'API_STATUS_OK': 200,
			'API_STATUS_CREATED': 201,
			'API_STATUS_ACCEPTED': 202,
			'API_STATUS_FOUND': 302,
			'API_STATUS_BAD_REQUEST': 400,
			'API_STATUS_UNAUTHORIZED': 401,
			'API_STATUS_FORBIDDEN': 403,
			'API_STATUS_NOT_FOUND': 404,
			'API_STATUS_NOT_ALLOWED': 405,
			'API_STATUS_NOT_ACCEPTABLE': 406,
			'API_STATUS_CONFLICT': 409,
			'API_STATUS_INTERNAL_ERROR': 500,
			'API_STATUS_NOT_IMPLEMENTED': 501,
			'API_STATUS_SERVICE_UNAVAILABLE': 503,
			'API_STATUS_VERSION_NOT_SUPPORTED': 505
		}
		self.process = None

		self.logs_path = path.abspath(path.join(path.dirname(__file__), '..', 'Log/CCN/'))
		self.config_path = path.abspath(path.join(path.dirname(__file__), 'ibr.conf'))
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
		self._dump()
		return self.node.routing_info()

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

if __name__ == "__main__":
	pass
