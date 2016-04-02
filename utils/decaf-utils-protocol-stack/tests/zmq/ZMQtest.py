import unittest

import time
import zmq

from decaf_utils_protocol_stack.zmq_transport.zmq_transport_layer import ZeroActor, STRING


def server_handler(msg, msg_type):
    print "Message:", msg

def client_handler(msg, msg_type):
    pass

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.client = ZeroActor(endpoint="tcp://127.0.0.1:9999", server=False, type=zmq.DEALER)
        self.server = ZeroActor(endpoint="tcp://127.0.0.1:9999", server=True, type=zmq.DEALER)
        self.server.set_handler(server_handler)


    def test_something(self):
        self.client.send("hello", STRING)


        time.sleep(5)


if __name__ == '__main__':
    unittest.main()
