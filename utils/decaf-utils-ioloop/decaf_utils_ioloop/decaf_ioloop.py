##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import Queue
import threading
import logging

try:
    from pika.adapters.select_connection import IOLoop
    logging.info("Using pika")
except ImportError:
    logging.info("Couldn't import pika")
    from pika_ioloop import IOLoop



from threading import Thread,current_thread

import traceback

import logging
import os
from functools import wraps


# Commands to the loop
SIGNAL_QUEUE_PUT =  0x0001
SIGNAL_INTERRUPT =  0x0004
SIGNAL_ACTOR_STOPPED =  0x0008

# Use epoll's constants to keep life easy
READ    = 0x0001
WRITE   = 0x0004
ERROR   = 0x0008


def on_loop(f):

    @wraps(f)
    def wrap_f(self, *args, **kwargs):
        assert isinstance(self, DecafActor)
        if(current_thread(), DecafIOThread):
            return f(self, *args, **kwargs)
        else:
            self.call_on_loop(self.__dict__[f.__name__],*args, **kwargs)

    return wrap_f

class DecafActor(object):


    def __init__(self, loop=None, *args, **kwargs):
        self._pipe = None
        self._queue = None
        pass

    def call_on_loop(self, method, *args, **kwargs):

        def func():
            method(*args, **kwargs)

        self._queue.put(func)

        if self._pipe:
            os.write(self._pipe.fileno(), bytearray(SIGNAL_QUEUE_PUT))

    def init_pipe(self, queue, pipe):
        self._pipe = pipe
        self._queue = queue


class DecafEventHandler(object):

    def __call__(self, desc, events, error=None, write_only=False):
        pass

class DecafIOLoop(IOLoop):


    """
    A special ioloop which also polls a queue.
    """
    def add_handler(self, desc, handler, events):
        """
        Add a new fileno to the set to be monitored.

       :param int fileno: The file descriptor.
       :param method handler: What is called when an event happens.
       :param int events: The event mask.

       """
        for acceptor, poller in self._pollers:

            if acceptor(desc):
                poller.add_handler(desc, handler, events)
                self._handler_dict[desc] = poller
                return

        super(DecafIOLoop, self).__getattr__("add_handler")(desc, handler, events)

    def update_handler(self, desc, events):
        """
        Set the events to the current events.

        :param int fileno: The file descriptor.
        :param int events: The event mask.

        """
        poller = self._handler_dict[desc]
        if poller:
            poller.update_handler(desc, events)
            return

        super(DecafIOLoop, self).__getattr__("update_handler")(desc, events)
        


    def remove_handler(self, desc):
        """
        Remove a file descriptor from the set.

        :param int fileno: The file descriptor.

        """
        poller = self._handler_dict[desc]
        if poller:
            poller.remove_handler(desc)
            del self._handler_dict[desc]
            return

        super(DecafIOLoop, self).__getattr__("remove_handler")(desc)
        

    def close(self):
        self._closing = True


    def poll(self, write_only=False):

        self.poll_sockets(write_only=write_only)
        self.process_queue()

    def get_next_deadline(self):
        if self._queue.empty():
            return self.check_deadline()
        else:
            return 0

    def __init__(self, use_zero_mq=True):
        """

        :return:
        """

        super(DecafIOLoop, self).__init__()

        self._queue = Queue.Queue(maxsize=0)
        self._closing = False

        # As the pika guys couldn't use inheritance in the ioloop (for better performance), we need this ugly workaround
        # We create function pointers to store the methods of the subclass and then override them "manually"
        self.poll_sockets = self._poller.poll
        self._poller.poll = self.poll

        self.check_deadline = self._poller.get_next_deadline
        self._poller.get_next_deadline = self.get_next_deadline

        self.inpipe, self.cmdpipe = self.get_interrupt_pair()

        #Additional poller, e.g. for ZeroMQ
        self._pollers = list()
        self._handler_dict = dict()

        self.add_handler(self.inpipe.fileno(), self.handle_inpipe, READ)

        self.stopped = False

        self.semaphore = threading.Semaphore()



    def _get_poller(self):

        try:
            from zmq_poller import ZeroPoller
            print "Using ZeroMQ"
            return ZeroPoller()
        except ImportError as e:
            print "ZeroMQ cannot be imported"
            #ZMQ not available, taking other poller
            return super(DecafIOLoop, self)._get_poller()

    def add_poller(self, acceptor, poller):
        self._pollers.append((acceptor, poller))

    def start(self):
        try:
            super(DecafIOLoop, self).__getattr__("start")()
        finally:
            self.stopped = True
            if self.cmdpipe:
                self.cmdpipe.close()
            if self.inpipe:
                self.inpipe.close()


    def call_on_loop(self, method, *args, **kwargs):
        """
        This method lets you inject arbitrary code on the ioloop.

         The diffrence between this function and add_timeout(0, ...) is the following:

        # Run event loop
        while not self._stopping:
                self.poll()// <- returns after sth. was read/written OR max. one second has passed
                self.process_timeouts()

        add_timeout schedules your code to be executed after polling.

        This can take up one second of doing nothing (if there is nothing to be polled)

        until your code is executed and your code appears to be super slow.

        This method however, creates an event on the poller and calls your code truly ASAP.


        :param method:
        :param args:
        :param kwargs:
        :return:
        """

        def func():
            method(*args, **kwargs)

        self.semaphore.acquire()
        self._queue.put(func)

        if self.cmdpipe and not self.stopped:
            os.write(self.cmdpipe.fileno(),bytearray(SIGNAL_QUEUE_PUT))
        self.semaphore.release()


    def handle_inpipe(self, fd, events, error=None, write_only=False):
        cmd = None
        if self.inpipe:
            cmd = os.read(self.inpipe.fileno(),1)
            if cmd is bytearray(SIGNAL_QUEUE_PUT):
                self.process_queue()
            elif cmd is bytearray(SIGNAL_INTERRUPT):
                self.interrupt()


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

    def interrupt(self):
        pass


class DecafIOThread(Thread):

    def __init__(self, logger=None):

        super(DecafIOThread, self).__init__()
        self._actors = list()
        self.ioloop = DecafIOLoop()
        self._open_files = list()
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

        pass

    def register_actor(self, actor):
        assert isinstance(actor, DecafActor)
        self._actors.append(actor)
        pass

    def init_actors(self):

        def handle_queue(queue):

            def wrapped_handler(desc, events, **kwargs):
                cmd = os.read(inpipe.fileno(), 1)
                if cmd is bytearray(SIGNAL_QUEUE_PUT):
                    while not queue.empty():
                        try:
                            func = queue.get_nowait()
                            func()
                            pass
                        except Queue.Empty:
                            pass
                else:
                    pass

            return wrapped_handler

        for actor in self._actors:
            inpipe, cmdpipe = self.ioloop.get_interrupt_pair()
            queue = Queue.Queue(maxsize=0)
            actor.init_pipe(cmdpipe, queue)
            self._open_files.append(inpipe)
            self._open_files.append(cmdpipe)
            self.ioloop.add_handler(inpipe.fileno(), handle_queue(queue), READ)



    def run(self):
        """

        Start the server by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        try:
            print "StartLoop"
            self.ioloop.call_on_loop(self.init_actors)
            self.ioloop.start()
        except Exception as e:
            # TODO: Make something meaningful here
            traceback.print_exc()
            self.logger.exception('Exception while in IO-Loop ({0})'.format(e))
            #print "Error in I/O-Loop: {0}".format(e.message)
            pass
        except:
            # TODO: Make something meaningful here
            traceback.print_exc()
            self.logger.exception('Exception while in IO-Loop')
        finally:
            print "StopLoop"
            for filehandle in self._open_files:
                filehandle.close()
            self.logger.info('Stopped the asynchronous consumer')

    def stop_ioloop(self):
        self.ioloop.stop()
