__author__ = 'thgoette'

import decaf.utils.rabbitmq.rpc_layer.rpc_layer as rpc
import time

def echo(x):
    return x

def echo1(x, foo='bar'):
    return x,foo

def echo2(foo= 'bar'):
    return foo

def printer(x):
    print x

#--------------r1 calls r2-----------------------------


r1 = rpc.RpcLayer()
r2 = rpc.RpcLayer()

r2.register("print",  echo)
r2.register("print1", echo1)
r2.register("print2", echo2)

d = r1.call("print",2)
d1 = r1.call("print1",2,foo='lol')
d2 = r1.call("print2",foo='lol')

d.addBoth(printer)
d1.addBoth(printer)
d2.addBoth(printer)

#--------------r1 calls a function that doesn't exits----------------------------

d = r1.call("solveP=NP",2)
d.addErrback(printer)

#--------------r1 calls a function syncronous----------------------------


print "Calling Sync"

import twisted.internet.defer

@twisted.internet.defer.inlineCallbacks
def test():
    x = yield r1.call("print", 2)
    print "Inside Test:" + str(x)

test()