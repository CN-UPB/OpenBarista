import threading
import random

__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest

import decaf_utils_rpc.rpc_layer as rpc
from twisted.internet import defer


class InlineCallbacks(BasicTest):
    def setUp(self):
        super(InlineCallbacks, self).setUp()

        topicSet="abcdefg*"


        self.callerdict = dict()
        for i in range(100):
            print "Creating Thread {0}".format(i)
            self.callerdict[i] = rpc.RpcLayer()
            self.callerdict[i].subscribe("%s.%s.%s" % (random.choice(topicSet), random.choice(topicSet), random.choice(topicSet)), )
        print "All good"

    def tearDown(self):
        super(InlineCallbacks, self).tearDown()

        for i in range(100):
            print "Disposing Thread {0}".format(i)
            self.callerdict[i].dispose()
        print "All good"

    @wait
    def test_inlinecallbacks(self):
        print "Starting inlineCallback Test "

        lock = threading.Lock()
        l = list()
        l.append(0)

        master = defer.Deferred()
        master.addCallback(lambda x: x)

        def callback(result):

            print "Callback {0}: {1}".format(str(l[0]), str(result))
            self.assertEqual(result, 50)
            with lock:
                l[0] += 1
                if l[0] > 98:
                    master.callback(99)

        for i in range(100):
            print "Starting Thread {0}".format(i)
            d = self.caller.call("plus5times10", 0)
            d.addBoth(callback)

        return master


if __name__ == '__main__':
    unittest.main()
