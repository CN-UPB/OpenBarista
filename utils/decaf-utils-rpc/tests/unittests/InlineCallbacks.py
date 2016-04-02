__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest


class InlineCallbacks(BasicTest):

    @wait
    def test_inlinecallbacks(self):
        print "Starting inlineCallback Test "

        def callback(result):

            print "Callback: " + str(result)
            self.assertEqual(result, 50)

        d = self.caller.call("plus5times10", 0)
        d.addBoth(callback)
        return d

if __name__ == '__main__':
    unittest.main()
