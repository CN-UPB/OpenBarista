import json
import unittest

import time

from decaf_utils_rpc.rpc_layer import RpcLayer
from decaf_vnf_manager_adapter.decaf_vnfm_adapter import *

def wait(function):

    def call(*args,**kwargs):
        d = function(*args,**kwargs)
        while not d.called:
            pass
        return d.result

    return call


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.random_rpc = RpcLayer(host_url=u"amqp://127.0.0.1")
        self.adapter = VNFManagerAdapter()
        self.adapter.connect(url=u"amqp://127.0.0.1")
        self.file = open("testsrc/linux.vnfd","r")
        self.json_dict = json.load(self.file)
        self.descriptors = list()
        for vnfc in self.json_dict["vnf"]["VNFC"]:
            self.descriptors.append({key:value for key,value in vnfc.items() if key in ["events","auth","name"]})
        print self.descriptors

    def test_something(self):
        try:
            time.sleep(1)
            d = self.random_rpc.call("VNFManagerAdapter.create_vnf_manager", 1337, self.descriptors)
            while not d.called:
                pass
            time.sleep(1)
            for vnc in self.descriptors:
                d = self.random_rpc.call("1337.new_vnfc_instance", ip_address=u"127.0.0.1", vnfc_id=vnc["name"])
            while not d.called:
                pass
            self.assertEqual(d.result,"Hello, Is there anybody out there ???\n")
            try:
                i = raw_input()
            except KeyboardInterrupt:
                pass
        except:
            try:
                i = raw_input()
            except KeyboardInterrupt:
                pass



    def tearDown(self):
        print "Begin Down done"
        self.adapter.dispose()
        self.random_rpc.dispose()
        print "Tear Down done"


if __name__ == '__main__':
    unittest.main()
