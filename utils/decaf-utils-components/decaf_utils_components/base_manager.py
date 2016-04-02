##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from abc import abstractmethod

from decaf_utils_components import BasePlugin
from decaf_utils_protocol_stack import RpcLayer, JsonRpcMessageApplication


class BaseManager(BasePlugin):

    @abstractmethod
    def handle_unrouted_message(self):
         pass

    def add(self):
         pass

    def update(self):
         pass

    def delete(self):
         pass


    def connect(self, url=None, rpc=None, routing_key=None):
        """
        Connects to the broker and registers the annotated methods.

        There are two ways to connect to the broker:

            a. Specify the broker's URL and thereby create a new RPCLayer to connect.
            This will start a new thread and a new TCP Connection in the background

            b. Use an existing and already connected RPCLayer

        :param url: The broker's URL to which a new Connection will be established. Either this or the the rpc_layer mustn't be None
        :param rpc: An existing RPCLayer which will create new Channel for this Plugin. Either this or the the URL mustn't be None
        :param routing_key: A prefix for registered methods
        :return:
        """
        self.lock.acquire()
        try:
            self._before_connect(url=url, rpc=rpc, routing_key=routing_key)
            if rpc is None and url is not None:
                rpc = JsonRpcMessageApplication(host_url=url)
                self.logger.debug("Created RPC Layer")

            elif rpc is not None:
                rpc = rpc
                self.logger.debug("Connecting via existing rpc layer")

            else:
                raise BaseException("You must specify either url or rpc")

            if routing_key:
                self.routing_key = routing_key
            else:
                self.routing_key = self._underscore_name(self.__class__.__name__)
            self.set_rpc(rpc)
            self._after_connect()
        except BaseException as e:
            self.logger.error(e)
            raise e
        finally:
            self.lock.release()



    def set_rpc(self, value):
        """
        Sets a new value to the rpc property and handles registering/deregistering endpoints. Rpc names should look like
        this: '<component_name>.<function_name>'

        :param value:
        :return:
        """
        if self._rpc is not None:
            self.logger.debug('Deregistering endpoints...')
            for function in [self.add, self.update, self.delete]:
                self.rpc.deregister("%s.%s" % (self.routing_key, function))
            self.logger.debug('Endpoints deregistered')
        self._rpc = value
        if self._rpc is not None:
            self.logger.debug('Registering endpoints...')
            for function in [self.add, self.update, self.delete]:

                def callOnSelf(self, func):
                    def call(*args, **kwargs):
                        return func(self, *args, **kwargs)

                    call.func_name = func.func_name
                    return call

                self.rpc.register("%s.%s" % (self.routing_key, function), callOnSelf(self, function))

            self.logger.debug('Endpoints registered')
