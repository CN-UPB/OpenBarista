import time

from decaf_utils_components import BasePlugin, In
from decaf_utils_components import Endpoint


class TestPlugin(BasePlugin):

    __version__ = "zzz"
    
    def __init__(self):
        super(TestPlugin, self).__init__(logger=None)


    def _after_connect(self):
        time.sleep(1)
        self.other = Endpoint(TestPlugin, rpc=self.rpc, logger=self.logger)
        print self.other.doA("lol")
        print self.other.doA(5)

    @In("a", str)
    def doA(self, a):
        return a + " A "

    @In("b", int)
    def doB(self):
        pass


class BasePluginTest(unittest.TestCase):

    def test_deamonize(self):
        daemonize(PluginA, "test")