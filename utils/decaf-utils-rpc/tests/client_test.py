import threading

__author__ = 'thgoette'

i = list()

def printer(x):
    lock.acquire()
    i.append(0)
    print len(i)
    lock.release()

import decaf_utils_rpc.rpc_layer as rpc

lock = threading.Lock()

r = rpc.RpcLayer(host_url=u'amqp://131.234.41.2:5672')
for j in range(1):
    r.call("componentmanager.version").addBoth(printer)



print "Im waiting for JAVA, this may takes a while"

