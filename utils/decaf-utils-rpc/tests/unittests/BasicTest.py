import threading
import time
from twisted.internet import defer
import decaf_utils_rpc.rpc_layer as rpc

__author__ = 'thgoette'

import unittest



def wait(function):

    def call(*args,**kwargs):
        d = function(*args,**kwargs)
        while not d.called:
            pass
        return d.result

    return call


class BasicTest(unittest.TestCase):

    def setUp(self):

        def unnamed(x):
            return x

        def mixed(x, foo='bar'):
            return x,foo

        def named(foo= 'bar'):
            return foo

        def add(x,y):
            return x+y

        def multiply(x,y):
            return x*y

        def timeout(*args):
            time.sleep(300)
            return "I've been waiting a long time for this moment"


        @defer.inlineCallbacks
        def callbackCascade(x):
            print "Starting Cascade"
            plus5 = yield self.callee.call("add",x,5)
            print "First result is: {0}".format(plus5)
            self.assertEqual(plus5, x+5)
            times10 = yield self.callee.call("multiply", plus5, 10)
            print "Second result is: {0}".format(times10)
            self.assertEqual(times10, (x+5)*10)
            defer.returnValue(times10)

        self.caller = rpc.RpcLayer()
        self.callee = rpc.RpcLayer()

        open = list()
        open.extend(["unnamed","named","mixed","add","multiply","plus5times10", "timeout"])

        lock = threading.Lock()

        def waiter(name):
            print "Thread tries to get lock"
            lock.acquire()
            print name + " ready"
            open.remove(name)
            lock.release()


        self.callee.register("unnamed",unnamed).addCallback(waiter)
        self.callee.register("named", named).addCallback(waiter)
        self.callee.register("mixed", mixed).addCallback(waiter)
        self.callee.register("add", add).addCallback(waiter)
        self.callee.register("multiply", multiply).addCallback(waiter)
        self.callee.register("plus5times10", callbackCascade).addCallback(waiter)
        self.callee.register("timeout", timeout).addCallback(waiter)

        OK = False

        while not OK:
            lock.acquire()
            OK = (len(open) == 0)
            lock.release()

        print "Set Up done"

    def tearDown(self):
        print "Begin Down done"
        self.callee.dispose()
        self.caller.dispose()
        print "Tear Down done"

