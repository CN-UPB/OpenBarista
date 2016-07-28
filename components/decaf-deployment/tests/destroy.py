__author__ = 'Kristian Hinnenthal'

import time
import twisted.internet.defer as defer
import sys

def printer(x):
    print x

import decaf_utils_rpc.rpc_layer as rpc

r = rpc.RpcLayer(u'amqp://fg-cn-sandman1.cs.upb.de:5672')

scenario_instance_id = str(sys.argv[1])

@defer.inlineCallbacks
def doWork():
    result = (yield r.call("deployment.scenario_delete_instance",scenario_instance_id))
    print(result)
    r.dispose()

if __name__ == '__main__':
    doWork()