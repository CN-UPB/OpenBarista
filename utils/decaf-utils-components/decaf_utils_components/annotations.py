##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from functools import wraps
from contract import Input, Output, Contract


def In(name, type, precondition=None):
    def wrapper(f):
        @wraps(f)
        def _function(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        i = Input(name, type)
        if hasattr(f, 'contract'):
            contract = f.contract
            contract.addInput(i)
        else:
            contract = Contract(f.__name__)
            contract.addInput(i)

        _function.__dict__["contract"] = contract
        _function.func_name = f.func_name

        return _function

    if precondition and not callable(precondition):
        raise BaseException("Precondition must callable")

    return wrapper


def Out(name, type, postcondition=None):
    def wrapper(f):
        @wraps(f)
        def _function(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        o = Output(name, type)
        if hasattr(f, 'contract'):

            contract = f.contract
            contract.addOutput(o)
        else:
            contract = Contract(f.__name__)

        _function.__dict__["contract"] = contract
        _function.func_name = f.func_name
        return _function

    if postcondition and not callable(postcondition):
        raise BaseException("Postcondition must callable")

    return wrapper


def Name(name):
    def wrapper(f):
        @warps(f)
        def _function(self, *args, **kwargs):
            return f(self, *args, **kwargs)

        if hasattr(f, 'contract'):

            contract = f.contract
            contract.setName(name)
        else:
            contract = Contract(name)

        _function.__dict__["contract"] = contract
        _function.func_name = f.func_name
        return _function

    return wrapper
