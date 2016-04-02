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


class JsonRPCMessage(object):
    def get_as_json(self):
        pass

    def get_as_tuple(self):
        pass


class JsonRPCNotify(JsonRPCMessage):
    def __init__(self,
                 method=None,
                 id=None,
                 args=(),
                 kwargs={}):
        self._method = method
        self._id = id
        self._args = args
        self._kwargs = kwargs

    @property
    def get_args(self):
        return self._args

    @property
    def get_kwargs(self):
        return self._kwargs

    def get_as_tuple(self):
        return self._method, self._id, self._args, self._kwargs

    def __str__(self):
        s = "<JSON_RPC_NOTIFY> \n Method : {0}\n Parameters : {1},{2}\n ID: {3}\n".format(self._method, self._args,
                                                                                          self._kwargs, self._id)
        return s


class JsonRPCCall(JsonRPCMessage):
    def __init__(self, method=None, id=None, args=None, kwargs=None):
        self._method = method
        self._id = id
        self._args = args
        self._kwargs = kwargs

    @property
    def get_id(self):
        return self._id

    @property
    def get_args(self):
        return self._args

    @property
    def get_kwargs(self):
        return self._kwargs

    def get_as_tuple(self):
        return self._method, self._id, self._args, self._kwargs

    def __str__(self):
        s = "<JSON_RPC_CALL> \n Method : {0}\n Parameters : {1},{2}\n ID: {3}\n".format(self._method, self._args,
                                                                                        self._kwargs, self._id)
        return s


class JsonRPCResult(JsonRPCMessage):
    def __init__(self, result=None, id=None):
        self._result = result
        self._id = id

    @property
    def get_id(self):
        return self._id

    @property
    def get_result(self):
        return self._result

    def __str__(self):
        s = "<JSON_RPC_RESULT> \n Result : {0}\n ID: {1}\n".format(self._result, self._id)
        return s

    def get_as_tuple(self):
        return self._result, self._id


class JsonRPCError(BaseException, JsonRPCMessage):
    def __init__(self, code=None, id=None, message=None, args=None, kwargs=None):
        self._code = code
        self._id = id
        self._message = message
        self._args = args
        self._kwargs = kwargs

    @property
    def getArgs(self):
        return self._args

    @property
    def getKwArgs(self):
        return self._kwargs

    @property
    def get_id(self):
        return self._id

    @property
    def getMessage(self):
        return self._message

    @property
    def getCode(self):
        return self._code

    def __str__(self):
        return "<JSON_RPC_ERROR>\n ID: {0} \n Message : {1}".format(self.getCode, self.getMessage)

    def get_as_tuple(self):
        return self.getCode, self.get_id, self.getMessage, self.getArgs, self.getKwArgs


class ApplicationError(JsonRPCError):
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


class ParseError(JsonRPCError):
    @property
    def getMessage(self):
        return "Parse Error"

    @property
    def getCode(self):
        return -32700


class InvalidRequestError(JsonRPCError):
    @property
    def getMessage(self):
        return "Invalid Request Error"

    @property
    def getCode(self):
        return -32600


class MethodNotFoundError(JsonRPCError):
    def __init__(self, method_name, location="Server", id=None):
        super(MethodNotFoundError, self).__init__(code=-32601, message="Method-not-found Error", id=str(id))
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


class InvaildParameterError(JsonRPCError):
    @property
    def getMessage(self):
        return "Invalid Parameter Error"

    @property
    def getCode(self):
        return -32602


class InternalError(JsonRPCError):
    @property
    def getMessage(self):
        return "Internal Server Error"

    @property
    def getCode(self):
        return -32603


class CallbackQueueClosedError(JsonRPCError):
    @property
    def getMessage(self):
        return "The given callback queue couldn't be reached. Is caller down ?"

    @property
    def getCode(self):
        return 2


class VersionNotSupportedError(JsonRPCError):
    @property
    def getMessage(self):
        return "Version is not supported by the server"

    @property
    def getCode(self):
        return 505


class CallerOfflineError(JsonRPCError):
    @property
    def getMessage(self):
        return "Could not reach the caller of the method"

    @property
    def getCode(self):
        return 404


ERRORS = {
    -32700: ParseError,
    -32600: InvalidRequestError,
    -32601: MethodNotFoundError,
    -32602: InvaildParameterError,
    -32603: InternalError,
    0: JsonRPCError,
    1: ApplicationError,
    2: CallbackQueueClosedError,
    505: VersionNotSupportedError,
    404: CallerOfflineError
}
