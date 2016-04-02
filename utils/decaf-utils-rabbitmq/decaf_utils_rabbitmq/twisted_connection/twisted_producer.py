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

import pika
from pika import exceptions
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol,task
from threading import Thread,Lock


from twisted_thread_safe_channel import TwistedThreadSafeChannel
import logging


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)



class TwistedProducer(Thread):

    def __init__(self, amqp_ip = 'localhost', amqp_port = 5672, connectionParameters = None, callback=None, connect_on_start=True):
        super(TwistedProducer, self).__init__()
        self._amqp_ip = amqp_ip
        self._amqp_port = amqp_port
        if connectionParameters:
            self._connectionParameters = connectionParameters
        else:
            self._connectionParameters = pika.ConnectionParameters()
        self._connection = None
        self._callback = callback
        self._connect_on_start=connect_on_start
        #self._stopper = self.ReactorStopper()
        self.start()
        self._lock = Lock()
        print "Twisted Producer Created"


    def run(self):
        print "Starting Reactor"
        if self._connect_on_start:
            self._connect()
        if not reactor.running:
            reactor.run(installSignalHandlers=0)
        print "Stopped"

    def _connect(self):
        cc = protocol.ClientCreator(reactor, twisted_connection.TwistedProtocolConnection, self._connectionParameters)
        d = cc.connectTCP(self._amqp_ip, self._amqp_port)
        d.addCallback(lambda protocol: protocol.ready)
        d.addCallback(self._on_connect)
        d.addErrback(self._on_connect_failed)


    def _on_connect(self, connection):
        LOGGER.info(str(self) + "connected")
        self._connection = connection
        if callable(self._callback):
            self._callback(connection)

    def openChannel(self):
        d = self._connection.channel()
        deliverChannelToMe = defer.Deferred()
        d.addCallback(self._on_channel_open, deliverChannelToMe)
        return deliverChannelToMe

    def _on_channel_open(self, channel, deliverChannelToMe):
        print str(self) + "opened a new channel"
        ts_channel = TwistedThreadSafeChannel(channel)
        deliverChannelToMe.callback(ts_channel)


    def _on_connect_failed(self, fail = None):
        print "Connection fail"
        print fail

    def stopReactor(self):

        def saveStop():
            if reactor.running:
                reactor.stop()


        reactor.callFromThread(saveStop)


