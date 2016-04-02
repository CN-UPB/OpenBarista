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

from twisted.internet.defer import Deferred, inlineCallbacks
from multiprocessing.dummy import Pool

from decaf_utils_protocol_stack import JsonRpcMessageApplication
from decaf_utils_protocol_stack.json import JsonRPCCall, JsonRPCNotify, JsonRPCError, JsonRPCResult
from decaf_utils_protocol_stack.rpc.sync_result import sync


class RpcLayer(JsonRpcMessageApplication):
    def __init__(self, host_url=u"amqp://127.0.0.1", ioloop=None, **params):
        super(RpcLayer, self).__init__(host_url=host_url, ioloop=ioloop, **params)
        self._pending = dict()
        self._pool = Pool()
        self.msg_handler = None

    def send_result(self, receiver, result, id):

        exchange = str(receiver).split(".")[0]
        self.route(receiver, JsonRPCResult(result=result, id=id), exchange=exchange)

    def send_error(self, receiver, code, id, *args, **kwargs):
        self.route(receiver, JsonRPCError(code=code, id=id, args=args, kwargs=kwargs))

    def call(self, method, *args, **kwargs):

        corr_id = str(uuid.uuid4())
        ret = Deferred()
        self._pending[corr_id] = ret
        self.route(method, JsonRPCCall(method=method, args=args, kwargs=kwargs, id=corr_id))
        return ret

    def publish(self, routing_key, msg, **params):

        corr_id = str(uuid.uuid4())
        ret = Deferred()
        self._pending[corr_id] = ret
        self.route(routing_key, JsonRPCNotify(method=routing_key, args=(msg,)), **params)
        return ret

    def callSync(self, timeout, rpc_name, *args, **kwargs):

        @sync(timeout=timeout)
        def wrap():
            return self.call(rpc_name, *args, **kwargs)

        return wrap()

    def notify(self, method, *args, **kwargs):
        self.publish(method, JsonRPCNotify(method=method, args=args, kwargs=kwargs))

    def deregister(self, routing_key, **params):
        params["method"] = "anycast"
        super(RpcLayer, self).unsubscribe(routing_key, **params)

    def unsubscribe(self, routing_key, **params):
        super(RpcLayer, self).unsubscribe(routing_key, **params)

    def subscribe(self, routing_key, function_pointer, frame=False, **params):

        self.logger.debug("Subscribing to %s with params: %s" % (routing_key, params))

        if function_pointer is None:
            function_pointer = self.receive
        else:
            if not frame: function_pointer = self._make_handler(function_pointer)
            function_pointer = self.apply_in_pool(function_pointer)

        super(RpcLayer, self).subscribe(routing_key, function_pointer=function_pointer, **params)

    def register_direct(self, routing_key, msg_handler):
        pass

    def register(self, routing_key, function_pointer=None, **params):

        if function_pointer is None:
            function_pointer = self.receive
        else:
            function_pointer = self._make_handler(function_pointer)
            function_pointer = self.apply_in_pool(function_pointer)

        params = params or dict()
        params["method"] = "anycast"
        self._top_layer.subscribe(routing_key, function_pointer=function_pointer, **params)

    def receive(self, *args, **kwargs):
        self._pool.apply_async(func=self._receive, args=args, kwds=kwargs)

    def apply_in_pool(self, function):

        def apply_f(*args, **kwargs):
            self._pool.apply_async(func=function, args=args, kwds=kwargs)

        apply_f.func_name = function.func_name
        return apply_f

    def _make_handler(self, function):
        """

        This method creates a wrapper for the given "function".

        This serves two purposes:

        A) Send the result back to the caller.

        B) Create an environment for asynchronous RPC within function.

        :param function:
        :param reply_to:
        :param corr_id:
        :return:
        """

        # ----------------- INTERNAL FUNCTION ------------------------------------------------------------

        @inlineCallbacks
        def on_call(routing_key, message, sender=None, **params):

            assert self.logger

            if isinstance(message, JsonRPCCall):
                try:
                    self.logger.info("-------------------CALL TO COMPONENT-----------------------")
                    self.logger.info("Executing function '%s' with argument(s) %s and %s", function.func_name,
                                     message.get_args, message.get_kwargs)
                    res = yield function(*message.get_args, **message.get_kwargs)
                    # self._out_channel.basic_ack(delivery_tag=delivery_tag)
                    self.send_result(result=res, receiver=sender, id=message.get_id)
                except BaseException as e:
                    self.logger.info("----------------CALL TO COMPONENT FAILED---------------------")
                    self.logger.exception("Message: \n %s \n caused an Error: \n %s" % (message, e))
                    self.send_error(code=1, message=e.message, receiver=sender, id=message.get_id, args=e.args)
                except:
                    self.logger.info("-----------------CALL TO COMPONENT FAILED---------------------")
                    self.logger.exception("Message: \n %s \n caused an Error" % (message))
                    self.send_error(code=1, receiver=sender, id=message.get_id)

            if isinstance(message, JsonRPCNotify):
                try:
                    self.logger.info("--------------DELIVER EVENT TO COMPONENT---------------------------")
                    self.logger.info("Executing function '%s' with argument(s) %s and %s", function.func_name,
                                     message.get_args, message.get_kwargs)
                    function(*message.get_args, **message.get_kwargs)
                except BaseException as e:
                    self.logger.info("--------------DELIVER EVENT TO COMPONENT FAILED---------------------")
                    self.logger.exception("Message: \n %s \n caused an Error: \n %s" % (message, e))

        # ----------------- INTERNAL FUNCTION ------------------------------------------------------------

        return on_call

    def _receive(self, routing_key, message, sender=None, **params):

        if isinstance(message, JsonRPCResult):
            self.logger.info("----------------RECEIVED A RESULT---------------------")
            self.logger.info("Result received: \n %s" % (message))
            corr_id = message.get_id
            deferred = self._pending.get(corr_id, None)
            if deferred:
                deferred.callback(message.get_result)
                del self._pending[corr_id]

        if isinstance(message, JsonRPCError):
            self.logger.info("----------------RECEIVED AN ERROR---------------------")
            self.logger.exception("Error received: \n %s" % (message))
            corr_id = message.get_id
            deferred = self._pending.get(corr_id, None)
            if deferred:
                deferred.errback(message)
                del self._pending[corr_id]

        if self.msg_handler:
            self.msg_handler(routing_key, message, sender, **params)
        pass

    def get_transport_layer(self):
        return super(RpcLayer, self).get_transport_layer()

    def set_msg_handler(self, msg_handler):
        self.msg_handler = msg_handler
