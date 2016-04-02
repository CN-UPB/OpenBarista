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

from decaf_utils_rabbitmq.async_connection.rabbit_ioloop import RabbitConnection

__author__ = 'thorsten'

from async_connection.async_consumer import AsyncConsumer
from twisted.internet import defer
from decaf_utils_ioloop.decaf_ioloop import DecafIOThread
import urlparse


class ChannelNotReadyError(Exception):
    pass


class RabbitMQLayer(object):
    """
    This class is a generic interface to RabbitMQ.
    """

    def __del__(self):
        self.dispose()

    def disposeConsumer(self, tag):
        con = self._consumers.get(tag, None)
        if con:
            con.stop_consuming()

    def dispose(self):
        for tag in self._consumers:
            self.disposeConsumer(tag)
        self._connection.stop()


    def __init__(self, host_url=u'amqp://127.0.0.1:5672', logger=None, ioloop=None, parameters=None, on_connected=None):
        self._consumers = dict()
        self.ready=False
        self.callWhenReady = {}

        self._host_url = host_url
        url = urlparse.urlparse(host_url)

        self._host_ip = url.hostname
        if url.port:
            self._host_port = url.port
        else:
            self._host_port = 5762

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

        if ioloop is None:
            self.io = DecafIOThread()
            self._connection = RabbitConnection(host_url, ioloop=self.io.ioloop, logger=self.logger, parameters=parameters, on_connected=on_connected)
            self.io.start()
            self._connection.run()
        else:
            self._connection = RabbitConnection(host_url, ioloop=ioloop, logger=self.logger, parameters=parameters, on_connected=on_connected)
            self._connection.run()

    @property
    def getHostIP(self):
        return self._host_ip

    @property
    def getHostPort(self):
        return self._host_port

    def _twisted_ready(self, *args, **kwargs):
        self.ready = True
        for d in self.callWhenReady:
            res = self.callWhenReady[d]()
            if isinstance(res, defer.Deferred):
                res.chainDeferred(d)
            else:
                d.callback(res)


    def createProducer(self):

        def callback(channel):
            d.callback(channel)

        d = defer.Deferred()
        con = self._connection.new_channel(callback)
        return d


    def createConsumer(self, queue_name, consume_method, exchange = None, exchange_type = None, routing_key = None, exclusive=True, tag=None):
        """
        Creates a ansynchrounus consumer which listens on the given Queue.

        :param queue_name:
        :param consume_method:
        :param exchange:
        :param exchange_type:
        :param routing_key:
        :return:
        """
        def on_setup_done(tag=None):
            if tag is not None:
                self._consumers[tag] = con
                result = (tag,queue_name)
                d.callback(result)

        d = defer.Deferred()
        con = AsyncConsumer(self._connection, queue_name, consume_method, amqp_url=self._host_url, on_setup_done = on_setup_done, exchange = exchange, exchange_type = exchange_type, routing_key = routing_key, logger=self.logger, exclusive=exclusive, tag=tag)
        return d



