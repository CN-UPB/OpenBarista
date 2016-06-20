__author__ = 'Kristian Hinnenthal'

import time
import twisted.internet.defer as defer

def printer(x):
    print x

import decaf_utils_rpc.rpc_layer as rpc

r = rpc.RpcLayer(u'amqp://fg-cn-sandman1.cs.upb.de:5672')

@defer.inlineCallbacks
def doWork():
    result = (yield r.call("deployment.scenario_start","7df6fbc9754944088d50e52f1cc7209a","TestInstance","TestDescription",1,True))
    print(result)
    r.dispose()

if __name__ == '__main__':
    doWork()