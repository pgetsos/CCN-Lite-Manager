#!/usr/bin/python3.5

from logging import getLogger
from config import CLIENT_PROTO, MSG_WINFO
from mnclient import MNClient
import msgpack

_LOG = getLogger(__name__)
_DLOG = getLogger('dedalus_logger')

class ClientRunner(MNClient):

    def __init__(self, context, endpoint, service):
        MNClient.__init__(self, context, endpoint, service)
        #self.run_dummy_interface()
        #self.options = {'1': self.test_traffic}
        #self.options_descr = {'1': "test traffic between two (random) nodes"}
        self.test_traffic()
        return

    def on_message(self, msg):
        # [rp, ' ', CLIENT_PROTO, service, cmd, wid, reply_msg]

        _LOG.info("Received: %s" % repr(msg))
        # TODO see message parts

         # 1st part is empty
        msg.pop(0)

        # 2nd part is protocol version
        # TODO: version check
        proto = msg.pop(0)
        if proto != CLIENT_PROTO:
            pass
            # TODO raise exception. add this functionality to other classes too

        (service, cmd, wid_str, reply) = msg

        if cmd == MSG_WINFO:
            self.winfo = msgpack.unpackb(reply)# TODO check recieved messages.
            print(self.winfo) #DEBUG

        return reply

    def do(self, option):
        if option not in self.options.keys():
            print("Your option does not exist. To see options type 0")
            return
        return self.options[option]()

    def show_operations(self):
        for (key, value) in self.options_descr:
            print(key, value)

    def on_timeout(self):
        print('TIMEOUT!')
        _LOG.info("Timeout! No response from broker.")
        return

    def test_traffic(self):
        print("send")
        self.request([b'', self._proto_version, b'ho.stat', MSG_WINFO], 10000)
        print("send2")
        # get worker info
        # request a server in one worker
        # request a client in other worker
        # measure the bandwith
