__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest


class NamedParams(BasicTest):

    @unittest.expectedFailure
    @wait
    def test_MethNotFound(self):
        print "Starting Test with Named Parameters"

        def callback(result):
            print "Callback: " + str(result)
            self.assertEqual(result, False)

        d = self.caller.call("Solve_P=NP")
        d.addBoth(callback)
        return d

if __name__ == '__main__':
    unittest.main()
