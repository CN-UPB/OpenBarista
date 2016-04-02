import unittest
import json
import decaf_utils_vnfm.element_manager.implementation as em

class MyTestCase(unittest.TestCase):



    def setUp(self):
        self.jsonString = '{"after_startup" : ["echo {message}"]}'
        self.jsonDict= json.loads(self.jsonString);
        self.manager = em.GenericSSHElementManager(host='localhost',username='thgoette',password='wasser')
        self.manager.generate_methods(self.jsonDict)


    def test_after_startup(self):
        print "Testing: ",self.jsonDict["after_startup"]," with message=DECAF"
        output, error = self.manager.after_startup(message=u'DECAF')
        print "Output: ", output
        print "Errors: ", error
        self.assertEquals(output[0][0], u"DECAF\n")

if __name__ == '__main__':
    unittest.main()
