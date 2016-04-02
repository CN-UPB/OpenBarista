__author__ = 'Kristian Hinnenthal'

import json
import time
import tests.example_datatypes as ex
import twisted.internet.defer as defer

import decaf_utils_rpc.rpc_layer as rpc

r = rpc.RpcLayer(u'amqp://fg-cn-decaf-head1.cs.upb.de:5672')

@defer.inlineCallbacks
def doWork():

    result = (yield r.subscribe(""))

    r.dispose()

if __name__ == '__main__':
    doWork()