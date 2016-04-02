__author__ = 'thgoette'

def echo(x):
    return x + " from PYTHON"

import decaf_utils_rpc.rpc_layer as rpc

r = rpc.RpcLayer()

for i in range(10):
    print "Register {0}".format(i)
    r.register(str(i), echo)
