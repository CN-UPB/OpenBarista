__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest


class NamedParams(BasicTest):

    @wait
    def test_CallWithNamedParamters(self):
        print "Starting Test with Named Parameters"

        def callback(result):
            print "Callback: " + str(result)
            self.assertEqual(result, "bar")

        d = self.caller.call("named", foo="bar")
        d.addBoth(callback)
        return d

if __name__ == '__main__':
    unittest.main()
