##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import logging
import traceback
from abc import abstractmethod
from functools import wraps

"""
This module containes the basic classes for the network stuff
"""


class IProtocolLayer(object):
    """
    Generally, a protocol layer accepts messages of format A and converts them to format B.

    It may performs additional calls.

    """

    def dispose(self):
        pass

    def route(self, routing_key, msg, **params):
        """

        Routes the given message according to the given routing key.

        Note: It is assumed that there is exactly one peer who receives the message (1-to-1 communication)

        :param routing_key:
        :param msg:
        :param params:
        :return:
        """
        pass

    def register(self, routing_key, function_pointer=None, **params):
        """

        Register this peer to the given routing key.

        Upon receiving of a message, the given function pointer is called.

        Note: It is assumed that there is exactly one peer who receives the message (1-to-1 communication)

        :param routing_key:
        :param function_pointer:
        :param params:
        :return:
        """

        pass

    def publish(self, routing_key, msg, **params):
        """

        Publishes the given message according to the given routing key.

        Note: It is assumed that there is an indefinite number of peers who receive the message (1-to-n communication)

        :param routing_key:
        :param msg:
        :param params:
        :return:
        """

        pass

    def subscribe(self, routing_key, function_pointer, **params):
        """

        Register this peer to the given routing key.

        Upon receiving of a message, the given function pointer is called.

        Note: It is assumed that there is an indefinite number of peers who receive the message (1-to-n communication)

        :param routing_key:
        :param function_pointer:
        :param params:
        :return:
        """
        pass

    def unsubscribe(self, routing_key, **params):
        pass

    def add_receiver(self, function_pointer, routing_key=None, **params):
        pass

    def get_transport_layer(self):
        """
        Retrieves the lowest layer of the stack, which directly accesses the transport protocol.

        :return:
        """
        pass


class TransportLayer(IProtocolLayer):
    """
    A transport layer is a special protocol layer.

    The methods are the same, but some things SHOULD be considered:

    1. It is always the lowest part of the stack and provides an interface to the transport protocol, e.g. RabbitMQ or ZeroMQ.

    2. It is thread-safe, e.g. by implementing an Decaf Actor

    """

    def route(self, routing_key, msg, **params):
        pass

    def publish(self, routing_key, msg, **params):
        pass

    def subscribe(self, routing_key, function_pointer, **params):
        pass

    def add_receiver(self, function_pointer, routing_key=None, **params):
        pass


class ProtocolLayer(IProtocolLayer):
    """
    Convenienience Implementation for a protocol layer.

    It simply passes everything to the next layer
    """

    @abstractmethod
    def _process_incoming_message(self, routing_key, msg, sender=None, **params):
        """

        Processes an incoming message.

        A message is may converted in step or additional params are added.

        :param routing_key:
        :param msg:
        :param sender:
        :param params:
        :return:
        """
        pass

    @abstractmethod
    def _process_outgoing_message(self, routing_key, msg, **params):
        """

        Processes an outgoing message.

        A message is may converted in step or additional params are added.

        :param routing_key:
        :param msg:
        :param sender:
        :param params:
        :return:
        """
        pass

    @abstractmethod
    def _dispose(self, *args, **kwargs):
        self._next_layer.dispose()

    @abstractmethod
    def _new_handle(self, prev_handle):
        return prev_handle

    def __init__(self, next_layer, receive_func=None, logger=None, *args, **kwargs):
        assert isinstance(next_layer, IProtocolLayer)
        self._next_layer = next_layer
        self._receive_funcs = list()
        self._next_layer.add_receiver(self._receive)

        if receive_func:
            self.add_receiver(receive_func)

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

    def _receive(self, routing_key, msg, sender=None, **params):

        routing_key, msg, sender, params = self._process_incoming_message(routing_key, msg, params=params)
        for func in self._receive_funcs:
            func(routing_key, msg, sender, **params)

    def __getattr__(self, item):
        return getattr(self._next_layer, item)

    def route(self, routing_key, msg, **params):
        routing_key, msg, params = self._process_outgoing_message(routing_key, msg, **params)
        return self._new_handle(self._next_layer.route(routing_key, msg, **params))

    def publish(self, routing_key, msg, **params):
        routing_key, msg, params = self._process_outgoing_message(routing_key, msg, **params)
        self._next_layer.publish(routing_key, msg, **params)

    def subscribe(self, routing_key, function_pointer, **params):

        @wraps(function_pointer)
        def wrapped_function(routing_key, msg, **params):
            try:
                routing_key, msg, sender, params = self._process_incoming_message(routing_key, msg, **params)
                function_pointer(routing_key, msg, sender, **params)
            except:
                traceback.print_exc()

        self._next_layer.subscribe(routing_key, wrapped_function, **params)

    def unsubscribe(self, routing_key, **params):
        self._next_layer.unsubscribe(routing_key, **params)

    def add_receiver(self, function_pointer, routing_key=None, **params):
        assert callable(function_pointer)
        self._receive_funcs.append(function_pointer)

    def dispose(self):
        self._dispose()
        self._next_layer.dispose()

    def get_transport_layer(self):
        if isinstance(self, TransportLayer):
            return self
        else:
            return self._next_layer.get_transport_layer();


class Application(IProtocolLayer):
    """
    An Application is on top of a protocol and provides an API to non I/O Modules and Classes.
    """

    def __init__(self, transport_layer, *protocol_layers, **config):
        """

        Creates a new protocol stack

        :param transport_layer: The lowest layer.
        :param protocol_layers: The stack.
        :param config: Passed to every constructor.
        :return:
        """
        super(Application, self).__init__()
        self._transport_layer = transport_layer
        self._layers = list()
        self._top_layer = None
        prev = self._transport_layer
        for layer in protocol_layers:
            tmp_layer = layer(prev, **config)
            self._layers.append(tmp_layer)
            self._top_layer = tmp_layer
        self._top_layer.add_receiver(self.receive)

        if config.get("logger", None):
            self.logger = config["logger"]
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

    def route(self, routing_key, msg, **params):
        self._top_layer.route(routing_key, msg, **params)

    def publish(self, routing_key, msg, **params):
        self._top_layer.publish(routing_key, msg, **params)

    def subscribe(self, routing_key, function_pointer, **params):
        self._top_layer.subscribe(routing_key, function_pointer, **params)

    def unsubscribe(self, routing_key, **params):
        self._top_layer.unsubscribe(routing_key, **params)

    def dispose(self):
        self._top_layer.dispose()

    def get_transport(self):
        return self._transport_layer

    @abstractmethod
    def receive(self, routing_key, message, sender=None, **params):
        print "call"

    def __getattr__(self, item):
        self.logger.debug("Unkown function call, passing to next layer: %s" % self._top_layer.__class__.__name__)
        return getattr(self._top_layer, item)
