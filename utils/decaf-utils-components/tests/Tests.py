import unittest

from BasePluginTest import TestPlugin


class MyTestCase(unittest.TestCase):

    def test_connect(self):
        try:
            t = TestPlugin()
            t.connect(url=u"amqp://127.0.0.1")
            while True:
                t = input(">")
        except KeyboardInterrupt:
            t.dispose()

    def test_serialize(self):
        try:
            t = TestPlugin()
            print t.serialize()
        except KeyboardInterrupt:
            t.dispose()


if __name__ == '__main__':
    unittest.main()
