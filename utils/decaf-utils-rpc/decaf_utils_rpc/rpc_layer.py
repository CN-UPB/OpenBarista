##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import traceback

import sys

import time

__author__ = 'root'

import uuid
import json

from twisted.internet import defer

import sys

import pika

from decaf_utils_rabbitmq.rabbitmq_layer import RabbitMQLayer

import logging

import threading

from rpc_errors import *

import signal

from sync_result import *

from multiprocessing.dummy import Pool


# logging.basicConfig(level=logging.INFO)


class IRpcLayer(object):
    """

    """

    def call(self, rpc_name, *args, **kwargs):
        """
        Calls the remote method with the given parameters.

        Currently the rpc_name needs to be globally unique !!!

        This method returns a @{defer.Deferred} that fires when the
        result of an error arrives

        Internally it uses a JSON-RPC Call over RabbitMQ with rpc_name as routing key

        Example:
            'Calls the method "add" on plugin X and prints the result'

            d = call("PluginX.add", 1, 2)

            d.addCallback(lambda x : print x) <- this would print the result !

            d.addErrback(lambda x : print "Error: " + x) <- this would print the error !

        Note, that one can use inlineCallbacks for a cleaner call

        Example:

            from twisted.internet.defer import inlineCallbacks

            @inlineCallbacks
            def addSync(val1,val2):

                result = yield call("PluginX.add", val1, val2)

                //do something with the result

                result = yield call("PluginY.subtract", result, val2)


        This may looks synchrouns but it isn't !!!

        It only syntactic sugar, that makes the code look nicer !

        For synchronous calls use 'callSync'

        :param rpc_name: A unique name for the rpc_layer method, e.g. <PluginName>.<MethodName>
        :param args: An ordered list of arguments
        :param kwargs: A dict of named arguments
        :return: a @{twisted.internet.defer.Deferred}
        """
        pass

    def callSync(self, timeout, rpc_name, *args, **kwargs):
        """
        Same as 'call', but synchronous.

        The calling thread will block until:

        a) The result arrives and is returned
        b) A timeout occurs
        c) An exception arrives and is thrown

        :param timeout: Time (in seconds) to wait for the result, e.g. 10.0
        :param rpc_name: A unique name for the rpc_layer method, e.g. <PluginName>.<MethodName>
        :param args: An ordered list of arguments
        :param kwargs: A dict of named arguments
        :return: The result of the call
        :raises: RPCError
        """
        pass

    def notify(self, rpc_name, *args, **kwargs):
        """
        Calls the remote method with the given parameters.

        This does not return anything

        :param rpc_name: A unique name for the rpc_layer method, e.g. <PluginName>.<MethodName>
        :param args: An ordered list of arguments
        :param kwargs: A dict of named arguments
        :return: None
        """
        pass


    def register(self, rpc_name, function_ptr):
        """
        Registers the given function for the rpc_name, so that it is called whenever a call for that rpc_layer arrives

        The given function MUST return a result

        Currently the rpc_name needs to be globally unique !!!

        :param rpc_name: A unique name for the rpc_layer method, e.g. <PluginName>.<MethodName>
        :param function_ptr: A function to be called. It has to return a result
        :return: None
        """
        pass

    def deregister(self, rpc_name):
        """
        Deregisters the rpc.

        :param rpc_name:
        :return:
        """
        pass

    def publish(self, tag, *args, **kwargs):
        pass

    def subscribe(self, tag, function_ptr):
        """

        Subscribes for all publications which match the given tag.

        A tag is a ordered list of keyword separated by "."

        Instead of keyword, one can give a wildcard "*"

        Example

        :param tag:
        :param function_ptr:
        :return:
        """
        pass

    def unsubscribe(self, tag):
        pass

    def setJsonEncoder(self, encoder):
        """

        Sets the encoder for dumping given return objects into json

        :return:
        """
        pass


class RpcLayer(IRpcLayer):
    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>> Setup Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------


    def dispose(self):
        """
        Stops the IO-Loop and terminates all running threads.

        :return:
        """
        self.rabbit_mq.dispose()

    def __init__(self, host_url=u'amqp://127.0.0.1:5672', negotiateProtocol=True, id=None, logger=None):

        if logger is not None:
            self.logger = logger

        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)


        self.logger.info("Creating new RPC Layer")

        self._negotiateProtocol = negotiateProtocol

        self._pool = Pool()

        self.lock = threading.Lock()

        self.rabbit_mq = RabbitMQLayer(host_url=host_url, logger=self.logger)

        self._out_channel = None
        self._out_channel_ready = False
        self._rpc_channel_ready = False
        self._callback_channel_ready = False
        self._pending = {}
        self._handlers = {}

        self.jsonEncoder = None

        if id is None:
            self._id = uuid.uuid4()
        else:
            self._id = id

        self._callWhenReady = dict()

        def describe():
            ret = dict()
            ret['sdversion'] = 1.0
            ret['name'] = "PYTHON SERVER"
            ret['id'] = str(self._id)

            return ret

        self.register("system.describe", describe)


        # --------------------------------------
        # ----Setup all the RabbitMQ Stuff------
        # --------------------------------------

        def logReady():
            """
            Checks if all channels are ready and writes it to the log
            """
            if self._callback_queue_ready() and self._rpc_queue_ready() and self._out_queue_ready():
                self.logger.info("All Channels ready")

        def _setChannel(channel):

            """
            Called by RabbitMQ when the Twisted Channel is ready.
            """

            self.logger.info("Channel for outgoing calls is ready")
            self._out_channel = channel
            self._out_channel_ready = True
            self._out_channel.add_on_return_callback(self._on_return)
            self._execute_pending_calls()
            logReady()

        def _setChannelReady(result):

            """
            Called by RabbitMQ when the RPC or Callback Channel is ready.
            """

            tag, queue_name = result

            if queue_name is self._rpc_queue_name:
                self.logger.info("RPC Channel is ready")
                self._rpc_channel_ready = True
            elif queue_name is self._callback_queue_name:
                self.logger.info("Callback Channel is ready")
                self._callback_channel_ready = True
            self._execute_pending_calls()
            logReady()

        out_queue_defer = self.rabbit_mq.createProducer()
        out_queue_defer.addCallback(_setChannel)

        self._rpc_broker_name = "rpc_broker"

        self._rpc_queue_name = str(self._id) + '_INCOMING-CALLS'
        self._callback_queue_name = str(self._id) + '_CALLBACKS'

        # Create Queue for calls
        rpc_defer = self.rabbit_mq.createConsumer(self._rpc_queue_name, self._on_call, exchange=self._rpc_broker_name,
                                                  exchange_type="topic", routing_key=str(self._id) + '.#')
        rpc_defer.addCallback(_setChannelReady)

        # Create Queue for callbacks
        callback_defer = self.rabbit_mq.createConsumer(self._callback_queue_name, self._on_result)
        callback_defer.addCallback(_setChannelReady)

        self._tags = dict()

        #FUCK IT; JUST WAIT FOR THE CONNECTION TO BE READY
        while(not self._rpc_queue_ready()) or (not self._out_queue_ready()) or (not self._callback_queue_ready()):
            time.sleep(1)

    def __del__(self):
        self.dispose()

    # --------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Utility Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # --------------------------------------------------------------------------------------------

    def _addToPendingCalls(self, function, args, kwargs, condition_function):
        """
        Adds a new call to be executed later, because of the given condition.

        The given function will be called with the given parameters.

        The result is returned in a Deferred.

        The mandatory condition_function states when it is possible to call the function.

        :param function:
        :param args:
        :param kwargs:
        :param condition_function:
        :return:
        """

        d = defer.Deferred()
        self._callWhenReady[d] = (function, args, kwargs, condition_function)
        return d

    def _execute_pending_calls(self):
        """
        Checks if the conditions of the pending calls are furfilled and executes them.

        All executed calls are removed from the list.

        This call uses a lock and is therefore threadsafe, but may blocks for a longer period.

        :return:
        """

        toDelete = list()
        self.logger.debug("Queue size %d" % len(self._callWhenReady))
        for d in self._callWhenReady:
            method, args, kwargs, condition_function = self._callWhenReady[d]
            if condition_function():
                toDelete.append(d)
                self.logger.debug("Calling method %s (%s)from queue" % (method.func_name, args))
                res = method(*args, **kwargs)
                if isinstance(res, defer.Deferred):
                    res.chainDeferred(d)
                else:
                    d.callback(res)

        for d in toDelete:
            del self._callWhenReady[d]
        self.logger.debug("Queue size after %d" % len(self._callWhenReady))


    def _disjunct(self, *args):
        """
        Disjuncts the given arguments, i.e puts them all in OR-Relation.

        The arguments can be boolean literals, object references or a pointer to a callable.

        This method returns a function which evalutes the clause.

        Example:

        A <- Callable

        B <- Object Reference

        C <- Boolean Variable

        f = _disjunct(A,B,C)

        f() <- returns A() or (B is not None) or C

        :param args:
        :return:
        """

        def evalArgs():
            ret = False
            for a in args:
                if callable(a):
                    ret = ret or a()
                else:
                    ret = ret or a
            return ret

        return evalArgs

    def _conjunct(self, *args):
        """

        Disjuncts the given arguments, i.e puts them all in AND-Relation.

        The arguments can be boolean literals, object references or a pointer to a callable.

        This method returns a function which evalutes the clause.

        Example:

        A <- Callable

        B <- Object Reference

        C <- Boolean Variable

        f = _disjunct(A,B,C)

        f() <- returns A() and (B is not None) and C


        :param args:
        :return:
        """

        def evalArgs():
            ret = True
            for a in args:
                if callable(a):
                    ret = ret and a()
                else:
                    ret = ret and a
            return ret

        return evalArgs

    def _out_queue_ready(self):
        return self._out_channel_ready

    def _callback_queue_ready(self):
        return self._callback_channel_ready

    def _rpc_queue_ready(self):
        return self._rpc_channel_ready

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>> Parsing Utility Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------

    def _pack_args(self, args, kwargs):
        """

        Creates a datastructure which can be parsed as parameters for JsonRPC.

        If the kwargs are not empty, it creates named parameters.

        In that case it returns dictionary and the unnamed parameters (args) get their position as the key.

        Otherwise it creates a list with unnamed parameters.

        :param args:
        :param kwargs:
        :return:
        """

        if kwargs:
            arg_dict = {}
            i = 0
            for arg in args:
                arg_dict[i] = arg
                i += 1
            arg_dict.update(kwargs)
            return arg_dict
        else:
            return [x for x in args]

    def _unpack_args(self, params):
        """
        Parses the args and kwargs.

        :param params:
        :return:
        """
        # -------------Util method---------------------------
        def is_int(value):
            try:
                int(value)
                return True
            except:
                return False

        arg_max = -1

        args = []
        kwargs = {}

        if isinstance(params, list):

            args = params

        elif isinstance(params, dict):

            # Make KWargs
            for k in params:
                if not is_int(k):
                    kwargs[k] = params[k]
                elif int(k) > arg_max:
                    arg_max = int(k)

            # Make ARGS and make sure they are in order !
            for i in range(0, arg_max + 1):
                args.append(params[str(i)])

        return args, kwargs

    def setJsonEncoder(self, encoder):
        self.jsonEncoder = encoder

    def parseJSONRPC(self,message_body):

            # -------------Parse json---------------------------
            try:
                call_dict = json.loads(message_body)
            except Exception as e:
                self.logger.error("Parsing error occured")
                raise ParseError(e.message, e.args)

            params = {}
            try:
                method_name = call_dict['method']
                params = call_dict['params']
            except KeyError as e:
                self.logger.error("Invalid Request received")
                raise InvalidRequestError(e.message, e.args)

            corr_id = call_dict.get('id', None)

            # ---------Transform parameters in the right DS------

            try:
                args, kwargs = self._unpack_args(params)
            except Exception as e:
                self.logger.error("Invalid parameters")
                raise InvaildParamterError(e.message, e.args)

            return method_name, args, kwargs, corr_id

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Client Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------


    def notify(self, rpc_name, *args, **kwargs):

        if self._out_channel is None:

            self.logger.info(
                "Postponing the Notify via function {0} with parameters {1} and {2}, because the channel is not ready".format(
                    rpc_name, args, kwargs))

            d = self._addToPendingCalls(self.notify, (rpc_name,) + args, kwargs,
                                        self._conjunct(self._out_queue_ready, self._callback_queue_ready))
            return d
        else:

            self.logger.info("Notify via function {0} with parameters {1} and {2}".format(rpc_name, args, kwargs))

            arg_dict = self._pack_args(args, kwargs)
            # Create RPC CALL
            json_dict = {}
            json_dict['jsonrpc'] = 2.0
            json_dict['method'] = rpc_name
            json_dict['params'] = arg_dict

            # Create string
            json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

            self._out_channel.basic_publish(exchange=self._rpc_broker_name,
                                            routing_key=rpc_name,
                                            properties=pika.BasicProperties(
                                                content_type='application/json',
                                                reply_to=self._callback_queue_name,
                                            ),
                                            body=json_string)

    def call(self, rpc_name, *args, **kwargs):
        if not self._out_queue_ready or not self._callback_channel_ready:

            self.logger.info(
                "Postponing the Call of function {0} with parameters {1} and {2}, because the channel is not ready".format(
                    rpc_name, args, kwargs))

            d = self._addToPendingCalls(self.call, (rpc_name,) + args, kwargs,
                                        self._conjunct(self._out_queue_ready, self._callback_queue_ready))
            return d

        else:


            version = float(kwargs.get('version', 2.0))

            self.logger.info("Call function {0} with parameters {1} and {2}".format(rpc_name, args, kwargs))
            #print "Call function {0} with parameters {1} and {2}".format(rpc_name, args, kwargs)

            corr_id = str(uuid.uuid4())
            ret = defer.Deferred()
            self._pending[corr_id] = ret
            # Create RPC CALL
            json_dict = {}
            json_dict['method'] = rpc_name
            arg_dict = dict()

            if version == 2.0:
                json_dict['jsonrpc'] = 2.0
                arg_dict = self._pack_args(args, kwargs)

            elif version == 1.1:
                # print "Taking version " + str(version)
                json_dict['version'] = '1.1'
                arg_dict = self._pack_args(args, None)
            else:
                raise VersionNotSupportedError

            json_dict['params'] = arg_dict
            json_dict['id'] = corr_id

            # Create string
            json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

            self._out_channel.basic_publish(exchange=self._rpc_broker_name,
                                            routing_key=rpc_name,
                                            properties=pika.BasicProperties(
                                                content_type='application/json',
                                                reply_to=self._callback_queue_name,
                                                correlation_id=corr_id,
                                            ),
                                            mandatory=True,
                                            body=json_string)

            return ret

    def callSync(self, timeout, rpc_name, *args, **kwargs):

        @sync(timeout=timeout)
        def wrap():
            return self.call(rpc_name, *args, **kwargs)

        return wrap()

    def _on_result(self, channel, method, props, body):
        """

        Is called when the server answers the RPC Call.

        Could be both a result or an error.

        :param channel:
        :param method:
        :param props:
        :param body:
        :return:
        """

        # print body
        self.logger.info("Received a response: {0}".format(body))
        #print "Received a response: {0}".format(body)

        # import threading
        # print threading.current_thread()
        try:
            call_dict = json.loads(body)
            corr_id = call_dict['id']
            if corr_id in self._pending:

                if 'result' in call_dict:

                    self.logger.info("Received a valid result for call {0}".format(corr_id))

                    result = call_dict['result']

                    self._pool.apply_async(func=self._pending[corr_id].callback, args=(result,))

                    # self._pending[corr_id].callback(result)

                elif 'error' in call_dict:
                    err_dict = call_dict['error']
                    code = err_dict['code']
                    message = err_dict['message']
                    args, kwargs = self._unpack_args(err_dict['data'])

                    self.logger.exception("Received an error result for call {0}".format(corr_id))
                    Error = ERRORS.get(code, RPCError)
                    e = Error(args, kwargs)
                    self._pool.apply_async(func=self._pending[corr_id].errback, args=(e,))

                del self._pending[corr_id]
        except:
            self.logger.exception("Exception while deserialize a response")

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Server Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------

    def register(self, rpc_name, function_ptr):

        self.lock.acquire()
        if (self._out_channel is None) or (not self._rpc_queue_ready()):
            self.logger.info("Channel not ready for registering, call is postponed")
            d = self._addToPendingCalls(self.register, [rpc_name, function_ptr], {},
                                        self._conjunct(self._rpc_queue_ready, self._out_queue_ready))

        else:

            self.logger.info("Channels are ready for registering, call is executed")

            def deliverAckToMe(*args):
                d.callback(rpc_name)

            d = defer.Deferred()
            self.logger.info("Registering the method {0} for the rpc {1}".format(function_ptr, rpc_name))
            self._handlers[rpc_name] = function_ptr
            self._out_channel.queue_bind(callback=deliverAckToMe, exchange=self._rpc_broker_name,
                                         queue=self._rpc_queue_name,
                                         routing_key=rpc_name)
        self.lock.release()
        return d

    def deregister(self, rpc_name):
        # Delete the handler locally
        if rpc_name in self._handlers:
            del self._handlers[rpc_name]

        if (self._out_channel is None) or (not self._rpc_queue_ready()):
            self.logger.info("Channel not ready for deregistering, call is postponed")
            d = self._addToPendingCalls(self.deregister, [rpc_name], {},
                                        self._conjunct(self._rpc_queue_ready, self._out_queue_ready))
            return d
        else:

            def deliverAckToMe(*args):
                d.callback(rpc_name)

            d = defer.Deferred()
            self.logger.info("Deregistering the rpc {0}".format(rpc_name))
            self._out_channel.queue_unbind(callback=deliverAckToMe, exchange=self._rpc_broker_name,
                                           queue=self._rpc_queue_name,
                                           routing_key=rpc_name)
            return d

    def _on_call(self, channel, method, props, body):


        self.logger.info("Received: {0}".format(body))
        try:

            method_name,args,kwargs,corr_id = self.parseJSONRPC(body)

            if not corr_id:
                corr_id = str(props.correlation_id)

            if method_name in self._handlers:
                try:
                    if corr_id:
                        function = self.__execute_safe(self._handlers[method_name], props.reply_to, corr_id, method.delivery_tag)
                        # callback = self.__send_result_to(props.reply_to, corr_id)
                        self._pool.apply_async(func=function,
                                               args=args,
                                               kwds=kwargs)

                    else:
                        self._pool.apply_async(func=self._handlers[method_name],
                                               args=args,
                                               kwds=kwargs)
                except BaseException as e:
                    self.logger.error("Cannot queue function '%s' : %s",function.func_name, str(e))

            else:
                self.logger.exception("Method Not Found")
                raise MethodNotFoundError(method_name, location="Server", id=self._id)

        except RPCError as e:
            self._send_error(e, props.reply_to, props.correlation_id)

    def __execute_safe(self, function, reply_to, corr_id, delivery_tag):
        """

        This method creates a wrapper for the given "funtion".

        This serves two purposes:

        A) Send the result back to the caller

        B) Create an environment for asynchronous RPC within function

        :param function:
        :param reply_to:
        :param corr_id:
        :return:
        """



        @defer.inlineCallbacks
        def catch_and_reply(*args, **kwargs):
            try:
                self.logger.info("-------CALL TO COMPONENT-------")
                self.logger.info("Executing function '%s' with argument(s) %s and %s", function.func_name, args, kwargs)
                res = yield function(*args, **kwargs)
                #self._out_channel.basic_ack(delivery_tag=delivery_tag)
                self._send_result(res, reply_to, corr_id)
            except BaseException as e:
                self.logger.exception(e)
                wrapped_e = ApplicationError(e.message, e.args)
                self._send_error(wrapped_e, reply_to, corr_id)

        return catch_and_reply

    def __send_result_to(self, reply_to, corr_id):
        """

        :param reply_to:
        :param corr_id:
        :return:
        """

        def send(result):
            #print str(self._id) + " : " + str(result)
            self._send_result(result, reply_to, corr_id)

        return send

    def _send_result(self, result, reply_to, corr_id):
        """

        :param result:
        :param reply_to:
        :param corr_id:
        :return:
        """
        json_dict = {}
        json_dict['jsonrpc'] = 2.0
        json_dict['result'] = result
        json_dict['id'] = corr_id

        # Create string
        json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

        # print "Sending " +json_string
        self._out_channel.basic_publish(exchange='',
                                        routing_key=reply_to,
                                        properties=pika.BasicProperties(
                                            content_type='application/json',
                                            correlation_id=corr_id,
                                        ),
                                        mandatory=True,
                                        body=json_string)
        self.logger.info("Send result %s for the request with id %s back to component %s", result, corr_id, reply_to)

    def _send_error(self, exception, reply_to, corr_id, *args, **kwargs):
        """

        :param code:
        :param reply_to:
        :param id:
        :param args:
        :param kwargs:
        :return:
        """
        # Create error object
        error_dict = {}
        error_dict['code'] = exception.getCode
        error_dict['message'] = exception.getMessage
        arg_dict = self._pack_args(exception.getArgs, exception.getKwArgs)

        error_dict['data'] = arg_dict

        # Create RPC CALL
        json_dict = {}
        json_dict['jsonrpc'] = 2.0
        json_dict['error'] = error_dict
        json_dict['id'] = str(corr_id)

        # Create string
        json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

        self._out_channel.basic_publish(exchange='',
                                        routing_key=reply_to,
                                        properties=pika.BasicProperties(
                                            content_type='application/json',
                                            correlation_id=corr_id,
                                        ),
                                        body=json_string)

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> General RabbitMQ Return Method <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------


    def _on_return(self, *args):
        """
        This method is called when the RabbitMQ broker itself sends a method to this Peer.

        :param msg
        :return:
        """

        channel, method, properties, body = args
        self.logger.info("Received a message from Broker: {0}, {1}, {2}, {3},".format(channel, method, properties, body))

        def receive_error(e):
            error_dict = dict()
            error_dict['code'] = e.getCode
            error_dict['message'] = e.getMessage

            arg_dict = self._pack_args(e.getArgs, e.getKwArgs)

            error_dict['data'] = arg_dict

            # Create RPC CALL
            json_dict = dict()
            json_dict['jsonrpc'] = 2.0
            json_dict['error'] = error_dict
            json_dict['id'] = properties.correlation_id

            json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

            self._on_result(channel, method, properties, json_string)



        # Create error object

        try:
            call_dict = json.loads(body)
        except Exception:
            self.logger.error("Parsing error occured")
            e = ParseError()
            receive_error(e)
            return

        params = {}
        try:
            method_name = call_dict.get('method', None)
            params = call_dict.get('params', None)
        except KeyError as keyError:
                self.logger.error("Invalid Request received: %s", keyError)
                e = InvalidRequestError()
                receive_error(e)
                return

        self.logger.exception("Broker found no component for the RPC")
        if method_name is not None:
            e = MethodNotFoundError(method_name, location="Broker")
        else:
            e = CallbackQueueClosedError()
        receive_error(e)
        return

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Publish / Subscribe <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------


    def publish(self, tag, *args, **kwargs):
        self.notify(tag,*args,**kwargs)

    def subscribe(self, tag, function_ptr):

        d = defer.Deferred()

        def deliverQueueToMe(*args):
            d.callback((tag, function_ptr,))

        def unpacker(channel, method, properties, body):
            tag, args, kwargs, id = self.parseJSONRPC(body)
            args.insert(0, tag)
            self._pool.apply_async(func=function_ptr,
                                   args=args,
                                   kwds=kwargs)

        self.rabbit_mq.createConsumer(str(uuid.uuid4()), unpacker,
                                      exchange=self._rpc_broker_name,
                                      exchange_type="topic",
                                      routing_key=tag).addCallback(deliverQueueToMe)
        return d


    def unsubscribe(self, tag, function_ptr):
        pass


