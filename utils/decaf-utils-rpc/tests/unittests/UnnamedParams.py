import threading

__author__ = 'thgoette'

from BasicTest import BasicTest, wait
import unittest

class NullWriter(object):
    def write(*_, **__):
        pass

    def flush(*_, **__):
        pass

SETUP_COUNTER = 0

class UnnamedParams(BasicTest):

    def setUp(self):
        super(UnnamedParams, self).setUp()
        global SETUP_COUNTER
        SETUP_COUNTER += 1


    def test_CallWithUnamedParamters(self):
        print "Starting Test with unnamed parameters"

        mutex = threading.Condition()

        the_result = list()

        def callback(result):
            mutex.acquire()
            print "Got '{0}'/ Expected 'bar' !".format(str(result))
            self.assertEqual(result, "bar")
            print "Success !"
            the_result.append(result)
            mutex.notifyAll()
            mutex.release()

        d = self.caller.call("unnamed", "bar")
        d.addBoth(callback)
        mutex.acquire()
        print "Waiting for Callback"
        while not the_result:
            mutex.wait()
        mutex.release()
        return d

def suite():
    tests = []
    for _ in range(100):
        tests.append('test_one')

    return unittest.TestSuite(map(UnnamedParams, tests))


if __name__ == '__main__':
    results = unittest.TextTestRunner(stream=NullWriter()).run(suite())
    print dir(results)
    print 'setUp was run', SETUP_COUNTER, 'times'


