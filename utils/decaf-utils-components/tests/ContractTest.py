import unittest

from decaf_utils_components import *


class Example2(object):

    @Out("a", str)
    @Out("b", str)
    @Out("c", str)
    def test(self):
        print "self = ", self

class ExampleInterface(object):

    __metaclass__ = PluginInterface


    @Name("The Function 2")
    @In("param", "String")
    @Out("out", str)
    def func2(self, param, x=None, *args, **kwargs):
        print "self = ",self


class ExampleContract(ExampleInterface):

    __metaclass__ = DecafPlugin

    __version__ = 0.1
    def __init__(self):
        print "Now"

    @Name("The Function")
    @In("param","String")
    @Out("out", str)
    def func(self, lol, x = 1, y = 2):
            pass

    def func2(self, param, x=None, *args, **kwargs):
        pass

    def test_contact(self):
        print self.contract.__class__.__dict__["func"].__dict__
        print self.contract._contract_list
        print self.contract._contract_functions
        print self.another_contract.__class__.__dict__["func"].__dict__


    def test_2(self):
        ex = Example2()
        print "--------t2-------------"
        ex.test()
        print "--------//t2-------------"

if __name__ == '__main__':
    unittest.main()
