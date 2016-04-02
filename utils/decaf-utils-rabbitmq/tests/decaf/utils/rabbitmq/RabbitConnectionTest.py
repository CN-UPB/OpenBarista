from decaf_utils_ioloop.decaf_ioloop import DecafIOThread
from decaf_utils_rabbitmq.async_connection.async_consumer import AsyncConsumer
from decaf_utils_rabbitmq.async_connection.rabbit_ioloop import RabbitConnection

__author__ = 'thgoette'

import unittest
import time

class RabbitConnectionTestCase(unittest.TestCase):


    def test_channel(self):

        self.con = None

        def do():
            pass

        def do2():
            pass


        def on_exchange_declareok(self):
            print "EXCHANGE OK"

        def callback(channel):
             channel.exchange_declare(on_exchange_declareok,
                                       "trool",
                                       "topic")
        io = DecafIOThread()

        print "here"

        self.con = RabbitConnection(ioloop=io.ioloop)
        self.con.run()

        io.start()

        time.sleep(5)
        self.con.new_channel(callback)
        #time.sleep(10)

    def test_consumer(self):

        def on_setup_done(tag=None):
            print " setup done"
            #con.stop()


        def method(*args,**kwargs):
            print "trololololololol"

        io = DecafIOThread()
        con = RabbitConnection(ioloop=io.ioloop)
        con.run()
        io.setDaemon(True)
        io.start()
        consumer = AsyncConsumer(con,"TheQueue", method, on_setup_done = on_setup_done, exchange = "trool", exchange_type = "topic", routing_key = "trololol")
        try:
            i = raw_input("")
        except:
            print "signal"
            io.stop_ioloop()

if __name__ == '__main__':
    unittest.main()
