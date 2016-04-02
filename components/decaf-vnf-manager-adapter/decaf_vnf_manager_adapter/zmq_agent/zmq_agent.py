##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_utils_protocol_stack.zmq_transport.zmq_transport_layer import ZeroActor
import zmq

class ZmqAgent(object):

    def __init__(self, manager_endpoint):
        self.actor = ZeroActor(endpoint=manager_endpoint, server=False, type=zmq.DEALER)

    def do(self, method, interval=1000):
        self.actor.do_recurring(method, interval=interval)

    def on_message(self, handler):
        self.actor.set_handler(handler)

    def run_forever(self):
        pass

