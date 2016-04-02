##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

__author__ = 'thgoette'

class RPCError(BaseException):

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    @property
    def getArgs(self):
        return self._args

    @property
    def getKwArgs(self):
        return self._kwargs

    @property
    def getMessage(self):
        return "Error on Server"

    @property
    def getCode(self):
        return 0


class ApplicationError(RPCError):

    def __init__(self, msg, *args, **kwargs):
        self._message = msg
        self._args = args
        self._kwargs = kwargs


    @property
    def getMessage(self):
        return self._message

    @property
    def getCode(self):
        return 1


class ParseError(RPCError):

    @property
    def getMessage(self):
        return "Parse Error"

    @property
    def getCode(self):
        return -32700


class InvalidRequestError(RPCError):

    @property
    def getMessage(self):
        return "Invalid Request Error"

    @property
    def getCode(self):
        return -32600


class MethodNotFoundError(RPCError):

    def __init__(self, method_name, location="Server", id=None):
        super(MethodNotFoundError, self).__init__(method_name, location=location, id=str(id))
        self._method_name = method_name
        self._location = location
        self._id = str(id)

    @property
    def getMethodName(self):
        return self._method_name

    @property
    def getMessage(self):
        return "Method-not-found Error"

    @property
    def getCode(self):
        return -32601


class InvaildParamterError(RPCError):

    @property
    def getMessage(self):
        return "Invalid Parameter Error"

    @property
    def getCode(self):
        return -32602


class InternalError(RPCError):

    @property
    def getMessage(self):
        return "Internal Server Error"

    @property
    def getCode(self):
        return -32603


class CallbackQueueClosedError(RPCError):

    @property
    def getMessage(self):
        return "The given callback queue couldn't be reached. Is caller down ?"

    @property
    def getCode(self):
        return 2

class VersionNotSupportedError(RPCError):

    @property
    def getMessage(self):
        return "Version is not supported by the server"

    @property
    def getCode(self):
        return 505

ERRORS = {
        -32700: ParseError,
        -32600: InvalidRequestError,
        -32601: MethodNotFoundError,
        -32602: InvaildParamterError,
        -32603: InternalError,
        0: RPCError,
        1: ApplicationError,
        2: CallbackQueueClosedError,
        505: VersionNotSupportedError
    }