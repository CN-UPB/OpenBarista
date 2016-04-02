__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest
import twisted.internet.defer as defer


class PubSubOneKeyword(BasicTest):


    @wait
    def test_CallWithMixedParamters(self):
        print "Starting Test with Mixed Parameters"

        d = defer.Deferred()


        def callback(tag,result):
            print "Got Pub/Sub Content {0} for tag {1}".format(result,tag)
            #self.assertEqual(tag, "foo")
            self.assertEqual(result, "bar")
            d.callback("All is fine")

        d_sub = self.callee.subscribe("foo", callback)
        while not d_sub.called:
            pass

        self.caller.publish("foo", "bar")

        return d

if __name__ == '__main__':
    unittest.main()
