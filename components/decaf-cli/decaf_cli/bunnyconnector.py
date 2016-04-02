##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import sys

from decaf_utils_protocol_stack import RpcLayer
from decaf_utils_rpc.rpc_errors import RPCError
from twisted.internet import defer
from twisted.python.failure import Failure



__author__ = "Andreas Krakau"
__date__ = "$29-sep-2015 09:57:30$"


class BunnyConnector(object):
    def __init__(self, url, logger):
        self.logger = logger
        self.logger.debug('Creating BunnyConnector...')
        self._rpc = None
        self.rpc = RpcLayer(url, logger=logger)
        self.logger.debug('Created BunnyConnector')

    @property
    def rpc(self):
        return self._rpc

    @rpc.setter
    def rpc(self, value):
        self._rpc = value

    def call(self, name, function, args, kwargs):
        """
        Call a remote function.

        :param name: Name of the component, that provides the function.
        :param function: The name of the function.
        :param args: An array of arguments.
        :return: The response received from the RPC
        """
        self.logger.debug("Calling %s.%s" % (name, function))
        try:
            ret = self.rpc.callSync(600, '%s.%s' % (name, function), *args, **kwargs)
            return ret
        except RPCError as e:
            self.logger.error("Could not call function '%s' on component '%s'. Error: %s" % (function, name, e.getMessage))
        except:
            e = sys.exc_info()[0]
            self.logger.error("Could not call function '%s' on component '%s'. Error: %s" % (function, name, e))

    def __del__(self):
        if self.rpc is not None:
            self.rpc.dispose()
            self.rpc = None
