__author__ = 'thgoette'

import decaf_utils_rpc.rpc_layer as rpc
import time

import decaf_utils_rpc.sync_result

import twisted.internet.defer
import threading


def echo(x):
    #print threading.currentThread()
    return x


def echo1(x, foo='bar'):
    #print threading.currentThread()
    return x, foo


@twisted.internet.defer.inlineCallbacks
def echo2(foo='bar'):
    #print "Thread {1} on Server: {0}".format(foo, threading.currentThread())
    d1 = yield r1.call("print", 30)
    #result1 =  d1
    #print "Thread {1} on Server: {0}".format(result1, threading.currentThread())
    twisted.internet.defer.returnValue(d1)


@decaf_utils_rpc.sync_result.sync(timeout=10.0)
def callSync(rpc_name, *args, **kwargs):
    return r1.call(rpc_name, *args, **kwargs)


def printer(x):
    print x


# --------------r1 calls r2-----------------------------



r1 = rpc.RpcLayer()
r2 = rpc.RpcLayer()

r2.register("print", echo)
r2.register("print1", echo1)
r2.register("print2", echo2)

time.sleep(2)

d = r1.call("print", 2)
d1 = r1.call("print1", 2, foo='lol')
d2 = r1.call("print2", foo='lol')

d.addBoth(printer)
d1.addBoth(printer)
d2.addBoth(printer)

# --------------r1 calls a function that doesn't exits----------------------------

#d = r1.call("solveP=NP", 2)
#d.addErrback(printer)

# --------------r1 calls a function syncronous----------------------------


print "Calling Sync"

d4 = callSync("print", 2)
print "Sync: " + str(d4)

@twisted.internet.defer.inlineCallbacks
def test():
    d1 = r1.call("print", 30)
    result1 = yield d1
    print threading.currentThread()
    print "Test 1: {0}".format(result1)

    d2 = r1.call("print", 40)
    result2 = yield d2
    print threading.currentThread()
    print "Test 2: {0}".format(result1 + result2)
    twisted.internet.defer.returnValue(result1 + result2)

d5 = test()
print "InlineReturn: " + str(d5)

#r1.dispose()
#r2.dispose()