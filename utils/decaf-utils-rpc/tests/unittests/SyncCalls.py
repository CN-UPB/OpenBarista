import decaf_utils_rpc

__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest



class SyncCall(BasicTest):


    def test_CallWithUnamedParamters(self):

        print "Starting Test with unnamed parameters"

        d = self.callee.callSync(10,"unnamed", "bar")
        print "Got '{0}'/ Expected 'bar' !".format(str(d))
        self.assertEqual(d, "bar")
        print "Success !"

    @unittest.expectedFailure
    def test_timeout(self):

        print "Starting Test with expected timeout"

        d = self.callee.callSync(10,"timeout", "bar")
        print "Got '{0}'/ Expected 'bar' !".format(str(d))
        self.assertEqual(d, "bar")
        print "Success !"

if __name__ == '__main__':
    unittest.main()
