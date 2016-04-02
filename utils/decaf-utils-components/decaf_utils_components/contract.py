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


class Checkable(object):
    """
    Superclass for Inputs and Outputs that allows to check values against the given type and condition.
    """
    def __init__(self, name, type, condition):
        self.name = name
        self.type = type
        if condition:
            self.condition = condition
        else:
            self.condition = None

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getCondition(self):
        return self.condition

    def __str__(self):
        return " \n Name : {0}\n Type : {1} \n Condition : {2}".format(self.name, self.type, self.condition)

    def __call__(self, argument):
         try:

            if argument is None or isinstance(argument, self.type):

                if self.condition:
                    return self.condition(argument)
                else:
                    return True

            else:
                 raise BaseException("Your value %s for variable %s doesn't match the type %s" % (argument,self.name,self.type))
         except:
            raise BaseException("Your value %s for variable %s doesn't match the schema %s" % (argument,self.name,self.condition))

class Input(Checkable):

    def __init__(self, name, type, precondition = None):
        super(Input, self).__init__(name, type, precondition)

    def serialize(self):
        return {
            "name": self.name,
            "type": self.type,
            #"precondition": self.condition
        }



class Output(Checkable):
    def __init__(self, name, type, postcondition=None):
        super(Output, self).__init__(name, type, postcondition)

    def serialize(self):
        return {
            "name": self.name,
            "type": self.type,
            #"postcondition": self.condition
        }


class Contract(object):
    def __init__(self, name, inputs=None, outputs=None):
        # print "Making new Contract"
        self.name = name
        if inputs:
            self.inputs = inputs
        else:
            self.inputs = dict()
        if outputs:
            self.outputs = outputs
        else:
            self.outputs = dict()

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getInputs(self):
        return self.inputs

    def addOutput(self, output):
        self.outputs[output.getName()] = output

    def addInput(self, input):
        self.inputs[input.getName()] = input

    def getOutputs(self):
        return self.outputs

    def serialize(self):
        dct = dict()
        dct["name"] = self.name
        dct["input"] = [x.serialize() for x in self.inputs.values()]
        dct["output"] = [x.serialize() for x in self.outputs.values()]
        return dct





