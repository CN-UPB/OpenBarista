##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_utils_protocol_stack.json import ApplicationError

__author__ = 'thgoette'

from threading import Event
import weakref

import imp

from twisted.internet.defer import *

from functools import wraps
from twisted.python.failure import Failure


class SyncResult(object):
    """
    A blocking interface to Deferred results.
    This allows you to access results from Twisted operations that may not be
    available immediately, using the wait() method.
    In general you should not create these directly;
    """

    def __init__(self, deferred):
        """
        The deferred parameter should be a Deferred or None indicating
        _connect_deferred will be called separately later.
        """
        self._deferred = deferred
        self._value = None
        self._result_retrieved = False
        self._result_set = Event()
        if deferred is not None:
            self._connect_deferred(deferred)

    def _connect_deferred(self, deferred):
        """
        Hook up the Deferred that that this will be the result of.
        Should only be run in Twisted thread, and only called once.
        """
        self._deferred = deferred

        # Because we use __del__, we need to make sure there are no cycles
        # involving this object, which is why we use a weakref:
        def put(result, eventual=weakref.ref(self)):
            eventual = eventual()
            if eventual:
                eventual._set_result(result)
            else:
                # TODO: ErrorHandling
                pass

        deferred.addBoth(put)

    def _set_result(self, result):
        """
        Set the result of the EventualResult, if not already set.
        This can only happen in the reactor thread, either as a result of
        Deferred firing, or as a result of ResultRegistry.stop(). So, no need
        for thread-safety.
        """
        if self._result_set.is_set():
            return
        self._value = result
        self._result_set.set()

    def __del__(self):
        if self._result_retrieved or not self._result_set.isSet():
            return
        if isinstance(self._value, Failure):
            # err(self._value, "Unhandled error in EventualResult")
            pass

    def cancel(self):
        """
        Try to cancel the operation by cancelling the underlying Deferred.
        Cancellation of the operation may or may not happen depending on
        underlying cancellation support and whether the operation has already
        finished. In any case, however, the underlying Deferred will be fired.
        Multiple calls will have no additional effect.
        """
        self._deferred.cancel()

    def _result(self, timeout=None):
        """
        Return the result, if available.
        It may take an unknown amount of time to return the result, so a
        timeout option is provided. If the given number of seconds pass with
        no result, a TimeoutError will be thrown.
        If a previous call timed out, additional calls to this function will
        still wait for a result and return it if available. If a result was
        returned on one call, additional calls will return/raise the same
        result.
        """

        if timeout is None:
            timeout = 2 ** 31
        self._result_set.wait(timeout)
        # In Python 2.6 we can't rely on the return result of wait(), so we
        # have to check manually:
        if not self._result_set.is_set():
            raise TimeoutError()
        self._result_retrieved = True
        return self._value

    def wait(self, timeout=None):
        """
        Return the result, or throw the exception if result is a failure.
        It may take an unknown amount of time to return the result, so a
        timeout option is provided. If the given number of seconds pass with
        no result, a TimeoutError will be thrown.
        If a previous call timed out, additional calls to this function will
        still wait for a result and return it if available. If a result was
        returned or raised on one call, additional calls will return/raise the
        same result.
        """

        if imp.lock_held():
            try:
                imp.release_lock()
            except RuntimeError:
                # The lock is held by some other thread. We should be safe
                # to continue.
                pass
            else:
                # If EventualResult.wait() is run during module import, if the
                # Twisted code that is being run also imports something the result
                # will be a deadlock. Even if that is not an issue it would
                # prevent importing in other threads until the call returns.
                raise RuntimeError(
                        "EventualResult.wait() must not be run at module import time.")

        try:
            result = self._result(timeout)
        except TimeoutError:
            raise
        if isinstance(result, Failure):
            result.raiseException()
            pass
        return result


def sync(timeout=None):
    """
    Calls will be syncrounus and timeout after the given number of seconds (a float), raising a
    TimeoutError.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            d = function(*args, **kwargs)
            sync_result = SyncResult(d)
            try:
                result = sync_result.wait(timeout)
                return result
            except TimeoutError:
                sync_result.cancel()
                raise
            except ApplicationError as e:
                # print "Uhz:", e.getMessage
                raise
            except:
                raise

        wrapper.wrapped_function = function
        try:
            return wrapper
        except:
            raise

    return decorator
