import unittest

import time

from decaf_utils_protocol_stack import JsonRpcMessageApplication
from decaf_utils_protocol_stack.json import JsonRPCLayer, JsonRPCNotify, JsonRPCCall
from decaf_utils_protocol_stack.protocol_layer import Application
from decaf_utils_protocol_stack.rmq import RmqTransportLayer

def printer(routing_key, message, sender=None, **params):
        print "SUBSCRIPTION"
        print message
        print "Sender: ", sender

class TestApplication(JsonRpcMessageApplication):


    def receive(self, routing_key, message, sender=None, **params):
        print "RECEIVE"
        print message
        print "Sender: ", sender


class MyTestCase(unittest.TestCase):

    def setUp(self):

        self.caller = TestApplication(host_url=u'amqp://127.0.0.1')
        self.caller.subscribe("subscribtion", printer)
        self.caller.register("method", printer)
        time.sleep(1)

    def test_messages(self):
        pass
        self.caller.notify("subscribtion", 13)
        self.caller.call("method", 13)
        self.caller.call("nonsense", 13)


if __name__ == '__main__':
    unittest.main()
