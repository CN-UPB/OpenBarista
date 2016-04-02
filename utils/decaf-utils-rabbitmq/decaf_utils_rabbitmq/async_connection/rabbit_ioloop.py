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
import traceback

from decaf_utils_ioloop.decaf_ioloop import DecafIOThread, DecafActor
from decaf_utils_rabbitmq.async_connection.rabbit_thread_safe_channel import RabbitThreadSafeChannel

__author__ = 'thgoette'

from threading import current_thread, Lock
import logging
import pika
import Queue

from pika.adapters.select_connection import IOLoop

#LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) ''-35s %(lineno) -5d: %(message)s')
#self.logger = logging.getlogger(__name__)

logging.basicConfig()

class RabbitIOLoop(IOLoop):
    """
    A special ioloop which also polls a queue.
    """

    def close(self):
        self._closing = True

    def poll(self, write_only=False):
        self.poll_sockets(write_only=write_only)
        self.process_queue()

    def get_next_deadline(self):
        if self._queue.empty():
            return self.check_deadline()
        else:
            return 1

    def __init__(self):
        """

        :return:
        """
        super(RabbitIOLoop, self).__init__()
        self._queue = Queue.Queue(maxsize=0)
        self._closing = False

        # As the pika guys couldn't use proper inheritance in the ioloop, we need this ugly workaround
        # We create function pointers to store the methods of the subclass and then override them "manually"
        self.poll_sockets = self._poller.poll
        self._poller.poll = self.poll

        self.check_deadline = self._poller.get_next_deadline
        self._poller.get_next_deadline = self.get_next_deadline

    @property
    def get_queue(self):
        return self._queue

    def process_queue(self):
        """
        Excutes all messages from threads.
        """
        # Excute all pending calls
        while not self._queue.empty():
            try:
                func = self._queue.get_nowait()
                func()
                pass
            except Queue.Empty:
                pass


class ThreadSafeConnection(pika.SelectConnection):
    """
    A special connection
    where threads can put messages
    in a queue which is accessed by the ioloop
    """

    def __init__(self,
                 parameters=None,
                 on_open_callback=None,
                 on_open_error_callback=None,
                 on_close_callback=None,
                 stop_ioloop_on_close=True,
                 custom_ioloop=None,
                 thread_queue=None,
                 logger=None,
                 **kwargs
                 ):
        """Create a new instance of the Connection object.

        :param pika.connection.Parameters parameters: Connection parameters
        :param method on_open_callback: Method to call on connection open
        :param on_open_error_callback: Method to call if the connection cant
                                       be opened
        :type on_open_error_callback: method
        :param method on_close_callback: Method to call on connection close
        :param bool stop_ioloop_on_close: Call ioloop.stop() if disconnected
        :raises: RuntimeError

        """

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

        if custom_ioloop:
            ioloop = custom_ioloop
        else:
            ioloop= RabbitIOLoop()
        super(ThreadSafeConnection, self).__init__(parameters, on_open_callback,
                                                   on_open_error_callback,
                                                   on_close_callback,
                                                   stop_ioloop_on_close,
                                                   custom_ioloop=ioloop,
                                                   )

    def call_on_loop(self, method, *args, **kwargs):
        """


        :param method:
        :param args:
        :param kwargs:
        :return:
        """

        self.ioloop.call_on_loop(method, *args, **kwargs)
        return

    def _send_message(self, channel_number, method_frame, content=None):
        super(ThreadSafeConnection, self)._send_message(channel_number, method_frame, content=content)


class RabbitConnection(DecafActor):
    """
    This thread handles all I/O and marks the sole connection to the broker
    """

    def __init__(self, amqp_url=u'amqp://127.0.0.1', ioloop=None, logger=None, parameters=None, on_connected=None):

        super(RabbitConnection, self).__init__()
        self._connection = None
        self._url = amqp_url
        self._callWhenReady = list()
        self.lock = Lock()
        self._closing = False
        self.ioloop = ioloop
        self.parameters = parameters
        self.on_connected = on_connected
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)



    def __del__(self):
        self.stop()

    def _addToPendingCalls(self, function, args, condition_function):
        """

        Adds a new call to be executed later, because of the given condition.

        The given function will be called with the given parameters.

        The mandatory condition_function states when it is possible to call the function.

        :param function:
        :param args:
        :param kwargs:
        :param condition_function:
        :return:
        """

        self._callWhenReady.append((function, args, condition_function))

    def _execute_pending_calls(self):
        """

        Checks if the conditions of the pending calls are furfilled and executes them.

        All executed calls are removed from the list.

        This call uses a lock and is therefore threadsafe, but may blocks for a longer period

        :return:
        """
        self.lock.acquire()
        toDelete = list()
        for item in self._callWhenReady:
            method, args, condition_function = item
            if condition_function():
                toDelete.append(item)
                method(*args)

        for item in toDelete:
            self._callWhenReady.remove(item)

        self.lock.release()

    def new_channel(self, deliverChannelToMe):

        if isinstance(current_thread(), DecafIOThread):
            self._connection.channel(on_open_callback=self._wrap_channel_callback(deliverChannelToMe))
        elif self._connection and self._connection.is_open:
            self._connection.ioloop.call_on_loop(self.new_channel, self._wrap_channel_callback(deliverChannelToMe))
        else:
            self._addToPendingCalls(self.new_channel, (deliverChannelToMe,), lambda: self._connection.is_open)
            pass

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        self.logger.info('Connecting to %s', self._url)
        return ThreadSafeConnection(pika.URLParameters(self._url),
                                    self.on_connection_open,
                                    stop_ioloop_on_close=True,
                                    custom_ioloop=self.ioloop,
                                    logger= self.logger)

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        print "Connected to RMQ"
        self.logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.logger.info('Starting Custom IOLoop')
        self._execute_pending_calls()
        if(self.on_connected):
            self.on_connected(self.ioloop, self._url, self.parameters)

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        self.logger.info('Adding connection close callback')
        #self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        if self._closing:
            #self._connection.ioloop.stop()
            pass
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            #self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def _wrap_channel_callback(self, deliverChannelToMe):
        """

        :param deliverChannelToMe:
        :return:
        """

        def callback(channel):
            threadSafeChannel = RabbitThreadSafeChannel(channel, self._connection)
            deliverChannelToMe(threadSafeChannel)

        return callback

    def run(self):
        """

        Start the server by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        try:
            self._connection = self.connect()
            #self._connection.ioloop.start()


        except Exception as e:
            # TODO: Make something meaningful here
            traceback.print_exc()
            self.logger.exception('Exception while in IO-Loop ({0})'.format(e))
            #print "Error in I/O-Loop: {0}".format(e.message)
            pass
        finally:
            self.logger.info('Stopped the asynchronous consumer')

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        self.logger.info('Stopping the asynchronous ioloop')
        try:
            # This will stop the IO Loop when the close is successful
            self._closing = True
            # There is no method for flush or someting,
            # so i simply delay the destruction, such that all other calls are processed
            if not (self._connection.is_closed or self._connection.is_closing):
                self._connection.close()
        except BaseException as e:
            # TODO: Make something meaningful here
            #traceback.print_exc()
            self.logger.error('Exception while closing connection ({0})'.format(e))
            self.logger.exception(e)
            #print "Error while closing I/O-Loop: {0}".format(e)
            pass
        except:
            e = sys.exc_info()[0]
            self.logger.exception(e)
        finally:
            self.logger.info('Stopped the asynchronous ioloop')
