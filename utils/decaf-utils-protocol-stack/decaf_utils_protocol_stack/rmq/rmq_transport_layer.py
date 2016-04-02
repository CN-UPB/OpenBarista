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
import threading
import traceback
import uuid
import pika
from decaf_utils_protocol_stack import TransportLayer
from decaf_utils_rabbitmq.rabbitmq_layer import RabbitMQLayer


class BrokerReturnMessage(object):
    def __init__(self, reply_code, reply_text, message=None, properties=None):
        self.reply_code = reply_code
        self.reply_text = reply_text
        self.wrapped_message = message
        self.wrapped_message_properties = properties

    def __str__(self):
        s = "<BrokerReturnMessage>\n Code: {0}\n Description : {1}\n Message : {2}\n Message Properties : {3}".format(
                self.reply_code, self.reply_text, self.wrapped_message, self.wrapped_message_properties)
        return s


class RmqTransportLayer(TransportLayer):
    def __init__(self, host_url=u'amqp://127.0.0.1:5672',
                 negotiateProtocol=True,
                 user_id=None,
                 id=None,
                 logger=None,
                 ioloop=None,
                 domain=None,
                 parameters=None):
        """

        :param host_url:
        :param negotiateProtocol:
        :param user_id:
        :param id:
        :param logger:
        :param ioloop:
        :param admin_broker:
        :param parameters:
        :return:
        """

        if logger is not None:
            self.logger = logger

        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

        self.logger.info("Creating new RPC Layer")

        self._receive_funcs = list()

        self._negotiateProtocol = negotiateProtocol

        self.semaphore = threading.Semaphore(0)

        self.rabbit_mq = RabbitMQLayer(host_url=host_url,
                                       logger=self.logger,
                                       ioloop=ioloop,
                                       on_connected=lambda *args, **kwargs: self.semaphore.release())

        self.semaphore.acquire()

        self._out_channel = None
        self._out_channel_ready = False
        self._in_channel_ready = False
        self._pending = {}
        self._handlers = {}

        self._id = id or uuid.uuid4()
        self._user_id = user_id or "guest"
        self._domain_id = domain or self._user_id

        # ---------------------------------------------------------
        # ---------------Setup all the RabbitMQ Stuff--------------
        # ---------------------------------------------------------

        try:

            # ---------------------------------------------------------
            # 1: Setup channel for RPC Calls to the broker

            def _setChannel(channel):
                """
                Called by RabbitMQ when the Twisted Channel is ready
                """

                self.logger.info("Channel for outgoing calls is ready")
                self._out_channel = channel
                self._out_channel_ready = True
                self._out_channel.add_on_return_callback(self._on_return)
                self.semaphore.release()

            out_queue_defer = self.rabbit_mq.createProducer()
            out_queue_defer.addCallback(_setChannel)

            # Wait until the connection stands
            self.semaphore.acquire()

            # Broker for this plugin's domain
            self._domain_exchange_name = str(self._domain_id)

            # Broker for this plugin directly
            self._rpc_broker_name = str(self._domain_id) + "." + str(self._id)

            # Queue for Callbacks and Results
            self._in_queue_name = str(self._rpc_broker_name) + '.incoming'

            self._domain_unrouted = str(self._domain_id) + ".unrouted"

            self._tags = dict(
                    name=self._id,
                    domain=self._domain_id,
                    user_id=self._user_id,
            )

            # ---------------------------------------------------------
            # 2: Setup exchanges for plugin and domain

            # Default I/O Exchange for this plugin
            self._out_channel.exchange_declare(lambda *args, **kwargs: self.semaphore.release(),
                                               exchange=self._rpc_broker_name,
                                               auto_delete=True,
                                               exchange_type='topic',
                                               arguments={
                                                   u"alternate-exchange": unicode(self._domain_exchange_name)
                                               })

            # Listen for results
            self.semaphore.acquire()
            rpc_defer = self.rabbit_mq.createConsumer(self._in_queue_name,
                                                      self._on_message,
                                                      exchange=self._rpc_broker_name,
                                                      routing_key=self._in_queue_name)

            rpc_defer.addCallback(lambda *args, **kwargs: self.semaphore.release())

            # Exchange for domain wide messages
            self.semaphore.acquire()
            self._out_channel.exchange_declare(lambda *args, **kwargs: self.semaphore.release(),
                                               exchange=self._domain_exchange_name,
                                               auto_delete=True,
                                               exchange_type='topic',
                                               arguments={
                                                   u"alternate-exchange": self._domain_unrouted
                                               }
                                               )

            self.semaphore.acquire()
            self._out_channel.exchange_bind(lambda *args, **kwargs: self.semaphore.release(),
                                            destination=self._rpc_broker_name,
                                            source=self._domain_exchange_name,
                                            routing_key=self._in_queue_name
                                            )

            # ----------------------------------------------------------------------------------
            # 3: Create drain for unrouted messages



            self.semaphore.acquire()
            self._out_channel.exchange_declare(lambda *args, **kwargs: self.semaphore.release(),
                                               exchange=self._domain_unrouted,
                                               auto_delete=True,
                                               exchange_type='topic',
                                               )

            self.semaphore.acquire()
            self._out_channel.queue_declare(lambda *args, **kwargs: self.semaphore.release(),
                                            queue=self._domain_unrouted,
                                            auto_delete=True,
                                            )

            self.semaphore.acquire()
            self._out_channel.queue_bind(lambda *args, **kwargs: self.semaphore.release(),
                                         queue=self._domain_unrouted,
                                         exchange=self._domain_unrouted,
                                         routing_key='#'
                                         )

            # ----------------------------------------------------------------------------------

            self.semaphore.acquire()
        except BaseException as e:
            self.logger.error("Error while setting exchanges in RMQ: \n %s" % e)
            traceback.print_exc()
            raise e

    def _on_message(self, channel, method, props, body):

        for func in self._receive_funcs:
            func(channel, method, props, body)

    def _on_return(self, channel, method, props, body):
        return_msg = BrokerReturnMessage(method.reply_code, method.reply_text, body, props)
        self._on_message(channel, method, props, return_msg)

    def route(self, routing_key, msg, content_type=u'text/plain', corr_id=None, exchange=None, **params):

        if exchange is None:
            exchange = self._rpc_broker_name

        self._out_channel.basic_publish(exchange=exchange,
                                        routing_key=unicode(routing_key),
                                        properties=pika.BasicProperties(
                                                content_type=content_type,
                                                reply_to=self._in_queue_name,
                                                correlation_id=corr_id
                                        ),
                                        mandatory=True,
                                        body=msg)

    def publish(self, routing_key, msg, content_type=u'text/plain', **params):
        self.route(routing_key, msg, content_type)

    def get_exchange(self):
        return self._rpc_broker_name

    def subscribe(self, routing_key, function_pointer, **params):

        def unpacker(channel, method, properties, body):
            """
            A Standard Queue Handler from pika that reads
            the message and the frame from the queue and converts it into
            the right format for the ProtocolStack.

            :param channel:
            :param method:
            :param properties:
            :param body:
            :return:
            """

            params = dict(channel=channel, method=method, properties=properties)
            routing_key = method.routing_key
            sender = properties.reply_to
            try:
                function_pointer(routing_key, body, sender=sender, **params)
            except:
                traceback.print_exc()
                raise

        # Check if we need subscribe for anycast or a multicast

        consumer_tag = str(self._id) + "." + routing_key

        # Multicast is also default
        if not params or params["method"] == "multicast":

            # Register a specific queue for this plugin and this call
            queue = str(self._domain_id) + "." + str(self._id) + "." + routing_key

            self.rabbit_mq.createConsumer(queue, unpacker,
                                          exchange=self._rpc_broker_name,
                                          routing_key=unicode(routing_key),
                                          tag=consumer_tag)

            self._out_channel.exchange_bind(lambda *args, **kwargs: None,
                                            destination=self._rpc_broker_name,
                                            source=self._domain_exchange_name,
                                            routing_key=unicode(routing_key)
                                            )

        elif params["method"] == "anycast":

            # Register a specific queue for this plugin and this call
            queue = str(self._domain_id) + "." + routing_key

            self.rabbit_mq.createConsumer(queue, unpacker,
                                          exchange=self._domain_exchange_name,
                                          routing_key=unicode(routing_key),
                                          exclusive=False,
                                          tag=consumer_tag)

        elif params["method"] == "direct":

            self.rabbit_mq.createConsumer(routing_key, unpacker, tag=consumer_tag)

    def unsubscribe(self, routing_key, **params):

        # Check if we need unsubscribe for anycast or a multicast

        consumer_tag = str(self._id) + "." + routing_key
        self._out_channel.basic_cancel(consumer_tag=consumer_tag)

        # Multicast is also default
        if not params or params["method"] == "multicast":
            # Deregister a specific queue for this plugin and this call
            queue = str(self._domain_id) + "." + str(self._id) + "." + routing_key
            self._out_channel.queue_delete(queue=queue)

    def add_receiver(self, function_pointer, routing_key=None, **params):

        assert callable(function_pointer)

        def unpacker(channel, method, properties, body):
            params = dict(channel=channel, method=method, properties=properties)
            routing_key = method.routing_key
            sender = properties.reply_to
            try:
                function_pointer(routing_key, body, sender=sender, **params)
            except:
                traceback.print_exc()

        self._receive_funcs.append(unpacker)

    def get_rmq_control_channel(self):
        """
        Returns a Channel to RMQ over which new Exchanges, Queue, etc. can be created or bound.

        :return:
        """
        return self._out_channel

    def dispose(self):
        self.rabbit_mq.dispose()

    def bind(self, channel, method, properties, body):
        """
        Binds this Plugin to the given Queue.

        :param channel:
        :param method:
        :param properties:
        :param body: Name of an existing Queue
        :return:
        """
        channel.basic_consume(self.loopback, queue=body)

    def loopback(self, channel, method, properties, body):
        """
        Redirects the message to the plugin's own exchange, s.t. it is handled like any other message.

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        routing_key = method.routing_key
        channel.basic_publish(self._rpc_broker_name, routing_key, body, properties)
