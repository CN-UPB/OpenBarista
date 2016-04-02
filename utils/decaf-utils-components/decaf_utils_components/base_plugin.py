##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import datetime

import re
import logging
import threading
from abc import abstractmethod

from .meta_classes import DecafPlugin
from decaf_utils_protocol_stack import RpcLayer



class BasePlugin(object):
    """
    Core class for a plugin.
    """
    __metaclass__ = DecafPlugin

    __version__ = "0.1-dev1"


    def __init__(self, logger=None, config=None, **kwargs):
        """
        Initializes the logger and the RPC.

        :param logger:
        :return:
        """
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)
        self.lock = threading.Lock()
        self._rpc = None
        self.config = config
        self.logger.debug("Base Plugin created")

    def dispose(self):
        """
        Disposes the plugin and disconnects cleanly from the broker.

        :return:
        """
        self.lock.acquire()
        if self.rpc is not None:
            self.logger.debug("Dispose Plugin")
            self.rpc.dispose()
            self._rpc = None
        else:
            self.logger.debug("Disposed nothing")
        self.lock.release()


    def connect(self, url=None, rpc=None, routing_key=None):
        """
        Connects to the broker and registers the annotated methods.

        There are two ways to connect to the broker:

            a. Specify the broker's URL and thereby create a new RPCLayer to connect.
            This will start a new thread and a new TCP Connection in the background

            b. Use an existing and already connected RPCLayer

        :param url: The broker's URL to which a new Connection will be established. Either this or the the rpc_layer mustn't be None.
        :param rpc: An existing RPCLayer which will create new Channel for this Plugin. Either this or the the URL mustn't be None.
        :param routing_key: A prefix for registered methods.
        :return:
        """
        self.lock.acquire()
        try:
            self._before_connect(url=url, rpc=rpc, routing_key=routing_key)
            if rpc is None and url is not None:
                rpc = RpcLayer(host_url=url, logger=self.logger)
                self.logger.debug("Created RPC Layer")

            elif rpc is not None:
                rpc = rpc
                self.logger.debug("Connecting via existing rpc layer")

            else:
                raise BaseException("You must specify either url or rpc")

            if routing_key:
                self.routing_key = routing_key
            else:
                # Hack
                self.routing_key = "decaf_" + self._underscore_name(self.__class__.__name__)

            self.rpc = rpc
            self._after_connect()
        except BaseException as e:
            self.logger.error(e)
            raise e
        finally:
            self.lock.release()

    @abstractmethod
    def _after_connect(self):
        pass

    @abstractmethod
    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    @property
    def rpc(self):
        """
        The RPC Layer which is used for the connection to the broker.

        :return:
        """
        return self._rpc

    @rpc.setter
    def rpc(self, value):
        """
        Sets a new value to the rpc property and handles registering/deregistering endpoints. Rpc names should look like
        this: '<component_name>.<function_name>'.

        :param value:
        :return:
        """
        if self._rpc is not None:
            self.logger.debug('Deregistering endpoints...')
            for contract, function in self.__implemented_contracts__.items():
                self.rpc.deregister(contract)
            self.logger.debug('Endpoints deregistered')
        self._rpc = value
        if self._rpc is not None:
            self.logger.debug('Registering endpoints...')
            for contract, function in self.__implemented_contracts__.items():

                def callOnSelf(self, func):
                    def call(*args, **kwargs):
                        return func(self, *args, **kwargs)

                    call.func_name = func.func_name
                    return call

                self.rpc.register("%s.%s" % (self.routing_key, contract), callOnSelf(self, function))

            self.logger.debug('Endpoints registered')

    @staticmethod
    def _underscore_name(name):
        """
        Converts CamelCase to camel_case.

        Example:
        calculate_tablename('HTTPResponseCodeXYZ')
        'http_response_code_xyz'
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


    @classmethod
    def __name_camel_case__(cls):
        return cls._underscore_name(cls.__name__)

    def serialize(self):

        functions = list()
        contracts = list()

        result = {
            "version"   : {
                        "version" : self.__version__,
                        "date"    : "---"
            },
            "functions" : functions,
            "contracts" : contracts,
        }

        for contractname, function in self.__implemented_contracts__.items():
            functions.append({
                "name" : function.func_name,
                "contract" : contractname
            })

            contract = function.func_dict["contract"]
            contracts.append(contract.serialize())

        return result