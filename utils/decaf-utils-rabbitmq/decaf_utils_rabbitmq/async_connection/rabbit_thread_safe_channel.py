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

import functools
from pika.adapters.twisted_connection import *
from twisted.internet import defer

class RabbitThreadSafeChannel(object):
    """A wrapper wround TwistedChannel.

    All API methods of pika.Channel are wrapped, s.t. they are called on the reactor.

    As an effect, all communication with RabbitMQ
    is handled via the reactor and thus thread-safe !
    """
    API_METHODS =       ('exchange_declare', 'exchange_delete',
                        'queue_declare', 'queue_bind', 'queue_purge',
                        'queue_unbind', 'basic_qos', 'basic_get',
                        'basic_recover', 'tx_select', 'tx_commit',
                        'tx_rollback', 'flow', 'basic_cancel',
                        'basic_consume', 'queue_delete', 'basic_publish')


    def __init__(self, channel, ioloop):
        self.__channel = channel
        self.__closed = None
        self.__calls = set()
        self.__consumers = {}
        self._ioloop = ioloop
        channel.add_on_close_callback(self.channel_closed)

    def channel_closed(self, *args):
        pass

    def __callOnThread(self, name):
        """
        Wrap API method to make it run on the reactor thread. This way, we're threadsafe.
        """

        method = getattr(self.__channel, name)

        if not callable(method):
            raise Exception(method + " is not callable")

        #This is the deferred I return, hence all user callbacks are added to this.
        d = defer.Deferred()

        @functools.wraps(method)
        def writeToDef(*args,**kwargs):
            if not (self.__channel.is_closed or self.__channel.is_closing):
                res = method(*args,**kwargs)
                if isinstance(res, defer.Deferred):
                    res.chainDeferred(d)
                else:
                    d.callback(res)
            else:
                pass
                #d.errback(Exception("Channel is closed"))


        @functools.wraps(writeToDef)
        def wrapped_method(*args, **kwargs):
            #print "Method " + str(name) + " with args: " + str(args) + " and kwargs: " + str(kwargs) + " is called on reactor"
            self._ioloop.call_on_loop(writeToDef, *args, **kwargs)
            return d

        return wrapped_method


    def __getattr__(self, name):
        # Wrap methods defined in WRAPPED_METHODS, forward the rest of accesses
        # to the channel.

        if name in self.API_METHODS:
            return self.__callOnThread(name)
        return getattr(self.__channel, name)

