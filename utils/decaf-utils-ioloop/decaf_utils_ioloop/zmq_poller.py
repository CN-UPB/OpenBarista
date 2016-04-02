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
from collections import defaultdict
try:
    from zmq.eventloop.ioloop import ZMQPoller
    from zmq.eventloop.ioloop import IOLoop
except ImportError:
    logging.info("ZeroMQ not found. Using fallback")
    raise ImportError

try:
    from pika.adapters.select_connection import SelectPoller, dictkeys
except ImportError:
    logging.info("pika not found. Using fallback")
    from pika_ioloop import SelectPoller, dictkeys

from collections import defaultdict
import errno




# Use epoll's constants to keep life easy
READ = 0x0001
WRITE = 0x0004
ERROR = 0x0008

class ZeroPoller(SelectPoller):

    def __init__(self):
        super(ZeroPoller, self).__init__()
        self._zmq_poller = ZMQPoller()


    @staticmethod
    def _map_events(events):
        """translate IOLoop.READ/WRITE/ERROR event masks into zmq-transport.POLLIN/OUT/ERR"""
        z_events = 0
        if events & IOLoop.READ:
            z_events |= READ
        if events & IOLoop.WRITE:
            z_events |= WRITE
        if events & IOLoop.ERROR:
            z_events |= ERROR
        return z_events


    @staticmethod
    def _remap_events(z_events):
        """translate zmq-transport.POLLIN/OUT/ERR event masks into IOLoop.READ/WRITE/ERROR"""
        events = 0
        if z_events & READ:
            events |= IOLoop.READ
        if z_events & WRITE:
            events |= IOLoop.WRITE
        if z_events & ERROR:
            events |= IOLoop.ERROR
        return events

    def update_handler(self, fileno, events):

        for ev in (READ, WRITE, ERROR):
            if events & ev:
                self._fd_events[ev].add(fileno)
            else:
                self._fd_events[ev].discard(fileno)

        self._zmq_poller.modify(fd=fileno, events=self._remap_events(events))

    def poll(self, write_only=False):
        """
        Check to see if the events that are cared about have fired.

        :param bool write_only: Don't look at self.events, just look to see if
            the adapter can write.

        """
        while True:
            zeroevents = list()
            try:

                zeroevents =  self._zmq_poller.poll(self.get_next_deadline())
                # print zeroevents
                break
            except Exception as e:
            # Depending on python version and IOLoop implementation,
                    # different exception types may be thrown and there are
                    # two ways EINTR might be signaled:
                    # * e.errno == errno.EINTR
                    # * e.args is like (errno.EINTR, 'Interrupted system call')
                    if hasattr(e,"errno"):
                        err = e.errno
                    else:
                        err = e.args[0]

                    if err == errno.EINTR:
                        continue
                    else:
                        raise

        fd_event_map = defaultdict(int)
        for (fd,events) in zeroevents:
            fd_event_map[fd] = self._map_events(events)

        for fileno in dictkeys(fd_event_map):
            if fileno not in fd_event_map:
                # the fileno has been removed from the map under our feet.
                continue


            events = fd_event_map[fileno]
            for ev in [READ, WRITE, ERROR]:
                if fileno not in self._fd_events[ev]:
                    events &= ~ev

            if events:
                handler = self._fd_handlers[fileno]
                handler(fileno, events, write_only=write_only)