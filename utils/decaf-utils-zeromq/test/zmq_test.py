import unittest

import time

import zmq
from decaf_utils_ioloop.decaf_ioloop import DecafIOThread
from decaf_utils_zeromq.zmq_layer import ZmqActor
from zmq import Context
import zmq.sugar.socket


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.io = DecafIOThread()
        self.zmq_actor = ZmqActor()
        self.io.register_actor(self.zmq_actor)
        self.io.start()
        time.sleep(2)
        pass

    def test_something(self):



            socket = self.zmq_actor.new_socket(zmq.DEALER)

            port = socket.bind_to_random_port("tcp://127.0.0.1")

            print port
            print socket.type

            socket2 = self.zmq_actor.new_socket(zmq.DEALER)

            succ = socket2.connect("tcp://127.0.0.1:{0}".format(port))

            print succ

            succ = socket2.send_string("moin")

            print succ

            recv = socket.recv_string()
            print "Recieved", recv

            i = raw_input()




if __name__ == '__main__':
    unittest.main()
