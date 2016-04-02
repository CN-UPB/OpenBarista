##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import inspect
import traceback


class SchemaError(BaseException):

    def __init__(self, function_name, arg, violated_schema):
        self.function_name = function_name
        self.arg = arg
        self.violated_schema = violated_schema

    def __str__(self):
        return "SchemaError in function {0}. The given argument {1} doesn't match schema {2}".format(self.function_name,self.arg, self.violated_schema)


def _make_function_typesafe(f, contract):
    """

    Binds the given function to the given contract and makes it typesafe.

    That means:

        a. checks if the function's parameters match the contract(static)
        b. Upon call of the function it matches the values with the given schemas(dynamic)

    :param f:
    :param contract:
    :return: A wrapped function "f" that checks its input and output as given in the "contract"
    """

    def _function(*args, **kwargs):


        for arg, schema in zip(args,schemas_by_order):
            try:
                schema(arg)
            except:
                raise SchemaError(f.func_name, arg, schema)


        for key in kwargs:
            try:
                schemas_by_name[key](kwargs[key])
            except:
                raise SchemaError(f.func_name, kwargs[key], schemas_by_name[key])

        return f(*args, **kwargs)

    _function.__dict__['contract'] = contract
    args, varargs, keywords, defaults = inspect.getargspec(f)
    schemas_by_order = list()
    schemas_by_name = dict()

    all_args = list()
    if args[1:]:
        all_args = all_args + args[1:]
    if defaults:
        all_args = all_args + list(defaults)

    if len(all_args)>0:
        for arg in all_args:#Concat args w/o self and the defaults
            if arg:
                input = contract.getInputs().get(arg,None)
                if input:
                    schemas_by_order.append(input)
                    schemas_by_name[arg] = input
                else:
                    raise BaseException("The variable {0} doesn't appear as an input in method {1} !".format(arg,f.func_name))
    else: # Method signature is generic (*args, **kwargs)
        for name in contract.getInputs():
                    schemas_by_order.append(contract.getInputs()[name])
                    schemas_by_name[name] = contract.getInputs()[name]

    if defaults:
        #Check if the default values match the schema
        i = len(schemas_by_order)-1
        for default in reversed(defaults):
            schemas_by_order[i](default)
            i -= 1

    _function.func_name = f.func_name
    return _function


class PluginInterface(type):
    """
    Metaclass for a Plugin Template similar to Java's notion of Interfaces.

    Usage:

        a. Create a python class with "empty" methods
        b. Set PluginInterface as metaclass
        c. Annotate methods with Inputs and Outputs
        d. Comment Methods

    Now a plugin class, i.e. a subclass of BasePlugin, can inherit this interface and implement (some of) the methods

    Example:

        class Converter(object):

            __metaclass__ = PluginInterface

            @In(a, str)
            @Out(b, int)
            def convert(a):
                '''
                Converts a str to an int
                '''

        class ConverterImpl(BasePlugin,Converter):

            def convert(a):
                #Quick hack, works for the demo
                if a == "5":
                    return 5
                elif a == "4":
                    return 4
                elif a == "3":
                    return 3
                elif a == "2":
                    return 2
                elif a == "1":
                    return 1
                elif:
                    return 0



    """

    def __init__(cls, name, bases, dct):
        cls.__contracts__ = [(key,value) for (key,value) in dct.items() if hasattr(value,'contract') ]
        super(PluginInterface, cls).__init__(name, bases, dct)


class DecafPlugin(PluginInterface):
    """
    Metaclass for all Plugins.

    Each class with this metaclass has an attribute "__implemented_contracts__".

    That is a dict where all contracts which the class implements are stored with the according function.

    Important Note: For most use-cases the class 'BasePlugin' is sufficient
    """


    def __new__(meta, name, bases, dct):

        for base in bases:
            if hasattr(base, "__metaclass__"):
                if base.__metaclass__ is PluginInterface:
                    for key, value in base.__contracts__:
                            if dct.get(key, None):
                                dct[key] = _make_function_typesafe(dct[key], value.__dict__["contract"])
        dct["__implemented_contracts__"] = None
        return super(DecafPlugin, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):

        if dct.get("__version__") is None:
            raise BaseException("Plugin must have a field '__version__' !!!")
        else:
            cls.__version__ = dct.get("__version__")

        cls.contract_list = dict(
            contracts=[value.__dict__['contract'].serialize() for value in dct.values() if hasattr(value, 'contract')])
        cls.__implemented_contracts__ = {value.contract.getName(): value for value in dct.values() if hasattr(value, 'contract')}

        super(DecafPlugin, cls).__init__(name, bases, dct)
