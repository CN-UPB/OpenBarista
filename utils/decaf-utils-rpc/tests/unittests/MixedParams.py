__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest


class MixedParams(BasicTest):

    @wait
    def test_CallWithMixedParamters(self):
        print "Starting Test with Mixed Parameters"

        def callback(result):
            print "Callback: " + str(result)
            self.assertEqual(result, ["foo","bar"])

        d = self.caller.call("mixed", "foo", foo="bar")
        d.addBoth(callback)
        return d

if __name__ == '__main__':
    unittest.main()
