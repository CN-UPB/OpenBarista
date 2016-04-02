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


    def test_something(self):
            time.sleep(1)

            d = self.random_rpc.call("storage.get_vnf", options=[],filters={})

            while not d.called:
                pass
            code, list = d.result



            if code == 200 and len(list)>0:
                vnf_id = list[0]["uuid"]

                d = self.random_rpc.call("VNFManagerAdapter.create_vnf_manager", vnf_id)
                while not d.called:
                    pass
                time.sleep(1)

                d = self.random_rpc.call("storage.get_vm", options=[],filters={"vnf_id": vnf_id})
                while not d.called:
                    pass
                code, descriptors = d.result

                for vnc in descriptors:
                    d = self.random_rpc.call("{0}.new_vnfc_instance".format(vnf_id), vnc["name"], u"127.0.0.1",
                                             {"username" : "thgoette" , "password" : ""} )
                    while not d.called:
                        pass
                    self.assertEqual(d.result,[[u"Starting\n"]])


    def tearDown(self):
        print "Begin Down done"
        self.adapter.dispose()
        self.random_rpc.dispose()
        print "Tear Down done"


if __name__ == '__main__':
    unittest.main()
