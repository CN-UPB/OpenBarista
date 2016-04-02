import unittest
import os
import logging
import traceback
from jsonschema import validate as json_validate, ValidationError as json_validateError

from decaf_specification import Specification



class DescriptorValidatorTest(unittest.TestCase):

    def setUp(self):

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(level=logging.DEBUG)
        self.specification = Specification(logger=self.logger, daemon=None)

        self.trace = True
        self.single_test = ["dataplaneVNF2.vnfd", "webserver.yaml"]


    def test_all(self):

        # This is shorter: Just store the pointer to the function
        validate = self.specification.descriptorValidator
        path = os.getcwd() + "/descriptor/"
        success = True

        for desc in os.listdir(path):
            if desc.endswith(".yaml") or desc.endswith(".vnfd"):

                try:
                    print "Testing file: ", desc
                    code, parsed = validate(path + desc)
                    if parsed:
                        print "Test OK..."
                    else:
                        print "Validation FAILED..."
                except:
                    success = False
                    if(self.trace):
                        traceback.print_exc()
                    print "Test FAILED..."
            else:
                print "Unknown file ending: ", desc

        self.assertEqual(success, True)

    def test_single(self):
        # This is shorter: Just store the pointer to the function
        validate = self.specification.descriptorValidator
        path = os.getcwd() + "/descriptor/"
        success = True

        for desc in os.listdir(path):
            if desc in self.single_test:

                try:
                    print "Testing file: ", desc
                    code, parsed = validate(path + desc)
                    if parsed:
                        print "Test OK..."
                    else:
                        print "Validation FAILED..."
                except:
                    success = False
                    if(self.trace):
                        traceback.print_exc()
                    print "Test FAILED..."

        self.assertEqual(success, True)




if __name__ == '__main__':
    unittest.main()
