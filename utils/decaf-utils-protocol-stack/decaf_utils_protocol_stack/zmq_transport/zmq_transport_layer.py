##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_utils_ioloop.decaf_ioloop import DecafActor, DecafIOThread, READ, WRITE, ERROR, on_loop
from decaf_utils_protocol_stack import TransportLayer
from zmq import Context
import zmq

JSON = unicode("JSON")
BYTES = unicode("BYTES")
PYTHON = unicode("PYTHON")
STRING = unicode('STRING')


class ZeroActor(DecafActor):
    """
    A minimal Wrapper around a ZeroMQ Socket that turns it into a threadsafe actor.
    """

    def set_handler(self, handler):
        self.handled = True
        self.handler = handler

    def msg_handler(self, socket, events, **kwargs):

        if events & READ:
            msg_type = self.socket.recv_string()
            if msg_type in [JSON, BYTES, PYTHON, STRING]:
                msg = None
                if msg_type == JSON:
                    msg = self.socket.recv_json()
                elif msg_type == BYTES:
                    msg = self.socket.recv()
                elif msg_type == PYTHON:
                    msg = self.socket.recv_pyobj()
                elif msg_type == STRING:
                    msg = self.socket.recv_string()
                self.handler(msg, msg_type)
        else:
            pass

        if events & WRITE:
            pass

        if events & ERROR:
            pass

    @on_loop
    def send(self, msg, msg_type, **kwargs):

        if msg_type in [JSON, BYTES, PYTHON, STRING]:
            self.socket.send_string(msg_type)
            if msg_type == JSON:
                self.socket.send_json(msg, **kwargs)
            elif msg_type == BYTES:
                self.socket.send(msg, **kwargs)
            elif msg_type == PYTHON:
                self.socket.send_pyobj(msg, **kwargs)
            elif msg_type == STRING:
                self.socket.send_string(msg, **kwargs)
        else:
            return

    @on_loop
    def do_recurring(self, function, intervall=1000):

        def make_recurring_call(f):
            def recurring_call():
                f()
                self.io.ioloop.add_timeout(intervall, recurring_call)

            return recurring_call

        f = make_recurring_call(function)
        self.io.ioloop.add_timeout(intervall, f)

    @on_loop
    def run(self):

        if self.isserver:
            self.socket.bind(self.endpoint)
        else:
            self.socket.connect(self.endpoint)

        self.io.ioloop.add_handler(self.socket, self.msg_handler, READ)

    def __init__(self, loop=None, endpoint="tcp://127.0.0.1:9999", server=True, type=zmq.ROUTER):
        super(ZeroActor, self).__init__()
        self.ctx = Context.instance()

        self.isserver = server
        self.socket = self.ctx.socket(type)

        self.endpoint = endpoint

        if loop is None:
            self.io = DecafIOThread()
            self.io.register_actor(self)
            self.io.start()
            self.run()
        else:
            self.io = loop
            self.io.register_actor(self)
            self.run()
