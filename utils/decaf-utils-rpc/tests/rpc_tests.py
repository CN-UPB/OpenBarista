__author__ = 'thgoette'

import unittest

import decaf_utils_rpc.rpc_layer as rpc
import time
import twisted.internet.defer as defer
import threading

class RpcLayerBasicTests(unittest.TestCase):

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

        @defer.inlineCallbacks
        def callbackCascade(x):
            plus5 = yield self.callee.call("add",x,5)
            print "First result is: {0}".format(plus5)
            self.assertEqual(plus5, x+5)
            times10 = yield self.callee.call("multiply", plus5, 10)
            print "Second result is: {0}".format(times10)
            self.assertEqual(times10, (x+5)*10)
            defer.returnValue(times10)


        self.caller = rpc.RpcLayer()
        self.callee = rpc.RpcLayer()

        self.callee.register("unnamed",unnamed)
        self.callee.register("named", named)
        self.callee.register("mixed", mixed)
        self.callee.register("add", add)
        self.callee.register("multiply", multiply)
        self.callee.register("plus5times10", callbackCascade)

        time.sleep(1)


    def test_CallWithNamedParamters(self):
        print "Starting Test with Named Parameters"

        def callback(result):
            print "Callback: " + result
            self.assertEqual(result, "bar")

        d = self.caller.call("named", foo="bar")
        d.addBoth(callback)

    def test_CallWithUnamedParamters(self):
        print "Starting Test with unnamed"

        def callback(result):
            print "Callback: " + result
            self.assertEqual(result, "bar")

        d = self.caller.call("unnamed", "bar")
        d.addBoth(callback)

    def test_CallWithMixedParamters(self):
        print "Starting Test with Mixed Parameters"

        def callback(result):
            print "Callback: " + result
            self.assertEqual(result, ["foo","bar"])

        d = self.caller.call("mixed", "foo", foo="bar")
        d.addBoth(callback)

    def test_inlinecallbacks(self):
        print "Starting inlineCallback Test "

        mutex = threading.Condition()

        the_result = list()

        def callback(result):
            mutex.acquire()
            print "Callback: " + str(result)
            self.assertEqual(result, 50)
            the_result.append(result)
            mutex.notifyAll()
            mutex.release()

        mutex.acquire()
        d = self.caller.call("plus5times10", 0)
        d.addBoth(callback)
        d.called

        while not the_result:
            mutex.wait()
        mutex.release()
        self.assertEqual(the_result.pop(), 50)



if __name__ == '__main__':
    unittest.main()
