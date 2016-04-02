__author__ = 'thgoette'

def echo(x):
    return x + " from PYTHON"

import decaf.utils.rabbitmq.rpc_layer.rpc_layer as rpc

r = rpc.RpcLayer()

r.register("echo", echo)