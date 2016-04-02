import unittest
import json
from decaf_vnf_manager_adapter.ssh_vnf_manager.generic_vnf_manager import GenericSSHVNFManager

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.file = open("testsrc/dataplaneVNF2.vnfd","r")
        self.json_dict = json.load(self.file)
        self.manager = GenericSSHVNFManager()
        self.manager.configure("vnf_id",vnf_descs=self.json_dict["vnf"]["VNFC"])
        print self.json_dict

    def test_new_instance(self):
        print self.manager.new_vnfc_instance(vnfc_id="dataplaneVNF2-VM", ip_address="localhost")
        print self.manager.new_vnfc_interface(vnfc_id="dataplaneVNF2-VM")

    def test_new_interface(self):
        pass


if __name__ == '__main__':
    unittest.main()
