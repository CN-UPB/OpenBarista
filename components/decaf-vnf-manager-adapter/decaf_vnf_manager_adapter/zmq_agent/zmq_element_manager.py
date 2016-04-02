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
from decaf_utils_protocol_stack.zmq_transport.zmq_transport_layer import ZeroActor
from decaf_vnfm_adapter import GenericSSHElementManager




class AbtractZmqElementManager(GenericSSHElementManager):

    """
    Transfers the Agent Script to the machine and starts it
    """

    def _after_connect(self):
        super(AbtractZmqElementManager, self)._after_connect()
        self.zmq_server = ZeroActor()
        self.zmq_server.set_handler(self.on_message)


    @abstractmethod
    def on_message(self, message, content_type):
        pass
