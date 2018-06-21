# -*- coding: utf-8 -*-
import socket
from logging import getLogger
from os import path, makedirs

from parse import *

from config import *
from ext.sh import dtnd, dtninbox, dtnoutbox, killall, sudo, SignalException_SIGKILL, ErrorReturnCode_1, echo, dtnping

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
            self.process = dtnd('-c', self.config_path, '-v', _out=log_file, _bg=True)

            log_inbox_file = open(self.logs_path + '/dtninbox.log', "a")
            # TODO : Should this line stay here? (I believe yes but the could be used also on demand in HWTraffic)
            dtninbox('in', IBR_INBOX, _out=log_inbox_file,
                     _bg=True)  # todo --> separate killall command for this: see stop

        except ErrorReturnCode_1:
            return 'a dtnd instance was already running in this system'

    @staticmethod
    def stop():
        try:
            with mn_sudo:
                killall('dtnd')
                killall('dtninbox')
                # TODO: CAUTION ---> every dtn service should be killed separately
        except SignalException_SIGKILL:
            return 'dtnd daemon killed!'
        except ErrorReturnCode_1:
            return 'no running dtnd instance found'

    def _connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            self.fsock = self.socket.makefile()
            ans = self.fsock.readline()
            self.node.proto_info = parse(self.formats['IBR-DTN'], ans).named
            self.socket.send("protocol management\n")
            ans = self.fsock.readline()
            if str(self.status_codes['API_STATUS_OK']) not in ans:
                # TODO: what should we do if not 200?
                _LOG.debug("The ibr daemon did not answer as expected")

        except socket.timeout:
            raise

    def _disconnect(self):
        """Method called to terminate the TCP connection.

        :rtype: None
        """
        self.socket.close()

    def get_routing_info(self):
        self._dump()
        return self.node.routing_info()

    @staticmethod
    def get_current_interface():
        # TODO: get this dynamically
        return DEFAULT_INTEFACE

    def _dump(self):
        try:
            self._connect()
            stats_msgs = {'stats_info': "stats info\n",
                          'stats_bundles': "stats bundles\n",
                          'stats_conv': "stats convergencelayers\n",
                          'neighbors': "neighbor list\n"}
            for k, m in stats_msgs.iteritems():  # TODO this is python 2.7 method
                self.socket.send(m)
                ans = self.recvall(self.fsock, self.status_codes)
                if k == 'neighbors':
                    self.node.proto_state[k] = ans.splitlines()
                else:
                    self.node.proto_state[k] = parse(self.formats[k], ans).named
        except socket.error as err:
            return 0
        finally:
            self._disconnect()

    def get_node(self):
        """Method that returns the ibr node.

        :rtype: IBRNode
        """
        return self.node

    # TODO should we keep this method? Or should it be renamed?
    @staticmethod
    def recvall(fs, status_codes):
        if str(status_codes['API_STATUS_OK']) not in fs.readline():
            # TODO do something more usefull here
            _LOG.debug("Bad status code. Expected API_STATUS_OK.")
            return None

        data = fs.readline()
        ans = ''
        while len(data) > 1:
            ans += data
            data = fs.readline()
        return ans

    # TODO rename and implement these
    def send_traffic(self, MB, dtn_receiver):
        pass

    def send_traffic_until(self, nimutes, dtn_receiver):
        pass

    def send_files(self, num_of_files, dtn_receiver):
        # TODO: we may need --lifetime in the future or changes in the configuration file
        log_outbox_file = open(self.logs_path + '/dtnoutbox.log', "a")

        ''' METHOD 1: dtnsend
        for i in range(num_of_files):
            fname = 'm_'+str(i)
            message = 'message '+str(i)
            echo(message, _out=IBR_OUTBOX+fname) # bg is not needed i  guess
            dtnsend(dtn_receiver+'/in', IBR_OUTBOX+fname, _out=log_outbox_file, _bg=True)
        '''

        ''' METHOD 2: dtnoutbox'''
        dtnoutbox(IBR_SENDER, IBR_OUTBOX, dtn_receiver + '/' + IBR_RECEIVER, _out=log_outbox_file, _bg=True)
        for i in range(num_of_files):
            fname = 'm_' + str(i)
            message = 'message ' + str(i)
            echo(message, _out=IBR_OUTBOX + fname)

        return str(num_of_files) + " files were sent"

    def ping(self, dtn_node):
        # TODO + timer + sudo (?) + answer with the last line ping outputs??
        log_ping_file = open(self.logs_path + '/dtnping.log', "a")
        dtnping(dtn_node + '/echo', _out=log_ping_file, _bg=True)
        # TODO maybe return the last lines of the dtnping.log, or get them with some other way


if __name__ == "__main__":
    pass
