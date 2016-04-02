import unittest

import time

from twisted.internet.defer import Deferred

from BasicTest import BasicTest, wait

d = Deferred()

def on_event(routingkey,msg,sender,**prams):
        print prams
        print msg
        d.callback(None)

class PublishTest(BasicTest):

    @wait
    def test_publish(self):
        print "Starting Test: Publish"

        event = {"key": {
            "bla" : "blub",
            "ping": "pong",
            "ying": "yang",
            "Its gonna be legen...":{
                "...wait for it..." : "...dary"
            }
        }}

        self.callee.subscribe("event", on_event)
        time.sleep(3)
        self.caller.publish("event", event)
        return d

if __name__ == '__main__':
    unittest.main()
