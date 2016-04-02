__author__ = 'thgoette'

def printer(x):
    print x

import decaf.utils.rabbitmq.rpc_layer.rpc_layer as rpc

r = rpc.RpcLayer()

d = r.call("echo","1", version=1.1)

print "Im waiting for JAVA, this may takes a while"

d.addCallback(printer)