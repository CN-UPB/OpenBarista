##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import uuid
from threading import Semaphore

from abc import abstractmethod

from decaf_utils_protocol_stack.json import JsonRPCLayer, JsonRPCCall, JsonRPCNotify, JsonRPCResult, JsonRPCError
from decaf_utils_protocol_stack.management.management_messages import Add
from decaf_utils_protocol_stack.protocol_layer import Application
from decaf_utils_protocol_stack.rmq import RmqTransportLayer


class JsonRpcMessageApplication(Application):
    """
    This an intermediate class with a bit more freedom.
    It builds
    """

    def send_result(self, receiver, result, id):
        self.route(receiver, JsonRPCResult(result=result, id=id))

    def send_error(self, receiver, code, id, *args, **kwargs):
        self.route(receiver, JsonRPCError(code=code, id=id, args=args, kwargs=kwargs))

    def call(self, method, *args, **kwargs):
        self.route(method, JsonRPCCall(method=method, args=args, kwargs=kwargs))

    def notify(self, method, *args, **kwargs):
        self.publish(method, JsonRPCNotify(method=method, args=args, kwargs=kwargs))

    def register(self, routing_key, function_pointer=None, **params):
        if function_pointer is None:
            function_pointer = self.receive

        self.subscribe(routing_key, function_pointer=function_pointer, **params)

    @abstractmethod
    def receive(self, routing_key, message, sender=None, **params):
        # Hi Andreas, hier kommen alle RPCCALLS, RESULTS und ERRORS rein, die du ueber call,send_error  und send_result sendest

        # Subscribe is extra, siehe Oberklasse
        pass

    def __init__(self, host_url, ioloop=None, **params):
        super(JsonRpcMessageApplication, self).__init__(RmqTransportLayer(host_url=host_url, ioloop=ioloop, **params),
                                                        JsonRPCLayer, **params)
