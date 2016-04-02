__author__ = 'Kristian Hinnenthal'

import json
import time
import tests.example_datatypes as ex
import twisted.internet.defer as defer
import unittest

class MaStaServerTester(object):

    def __init__(self):
        self.rpc = rpc.RpcLayer(u'amqp://fg-cn-decaf-head1.cs.upb.de:5672')

    def test_deploy(self):
        result = self.rpc.callSync(10, "decaf_masta.deploy_scenario", ex.small_deploy_graph)
        print(result)

    def test_extend(self):
        result = self.rpc.callSync(10, "decaf_masta.extend_scenario", ex.small_add_graph)
        print(result)

    def test_shrink(self):
        result = self.rpc.callSync(10, "decaf_masta.shrink_scenario", ex.small_shrink_graph)
        print(result)

    def test_destroy(self):
        result = self.rpc.callSync(10, "decaf_masta.destroy_scenario", "SmallScenario")
        print(result)

    def end(self):
        self.rpc.dispose()

if __name__ == '__main__':

    tester = MaStaServerTester()

    #tester.test_deploy()
    #tester.test_extend()
    #tester.test_shrink()
    tester.test_destroy()

    tester.end()