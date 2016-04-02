import unittest
import json
from decaf_vnf_manager_adapter import GenericSSHVNFManager
from decaf_vnf_manager_adapter import GenericSSHElementManager

class MyTestCase(unittest.TestCase):



    def setUp(self):
        self.jsonString = '{"after_startup" : ["echo {message}"]}'
        self.jsonDict= json.loads(self.jsonString)
        self.manager = GenericSSHElementManager()
        #self.manager.generate_methods(self.jsonDict)



    def test_after_startup(self):
        print "Testing: ",self.jsonDict["after_startup"]," with message=DECAF"
        output, error = self.manager.after_startup(message=u'DECAF')
        print "Output: ", output
        print "Errors: ", error
        self.assertEquals(output[0][0], u"DECAF\n")

    def test_download(self):
        handle = self.manager.download_file("https://github.com/downloads/zeromq/pyzmq/pyzmq-2.2.0.1.tar.gz")


if __name__ == '__main__':
    unittest.main()
