##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import json
import uuid
from decaf_utils_protocol_stack.protocol_layer import ProtocolLayer
from decaf_utils_protocol_stack.json import *
from decaf_utils_protocol_stack.rmq.rmq_transport_layer import BrokerReturnMessage


class JsonRPCLayer(ProtocolLayer):
    """
    This layer is an implementation of the JSON RPC Protocol.
    """

    def __init__(self, next_layer, logger=None, json_encoder=None):
        super(JsonRPCLayer, self).__init__(next_layer, logger=logger)
        self.jsonEncoder = json_encoder

    def set_json_encoder(self, json_encoder):
        self.jsonEncoder = json_encoder

    # -----------------------------------------------------------------------------------------------
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>> Parsing Utility Methods <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # -----------------------------------------------------------------------------------------------

    def _pack_args(self, *args, **kwargs):
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

    def _convert_to_JSONRPC(self, method, id=None, args=None, kwargs=None):

        version = float(kwargs.get('version', 2.0))

        self.logger.info("Call function {0} with parameters {1} and {2}".format(method, args, kwargs))
        # print "Call function {0} with parameters {1} and {2}".format(rpc_name, args, kwargs)

        # Create RPC CALL
        json_dict = {}
        json_dict['method'] = method
        arg_dict = dict()

        if version == 2.0:
            json_dict['jsonrpc'] = 2.0
            arg_dict = self._pack_args(*args, **kwargs)

        elif version == 1.1:
            # print "Taking version " + str(version)
            json_dict['version'] = '1.1'
            arg_dict = self._pack_args(args, None)
        else:
            raise VersionNotSupportedError

        json_dict['params'] = arg_dict
        if id is not None:
            json_dict['id'] = id

        # Create string
        json_string = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

        return json_string

    def _convert_to_JSONRPC_Error(self, code, corr_id, message=None, *args, **kwargs):

        error_dict = {}
        error_dict['code'] = code
        error_dict['message'] = message
        arg_dict = self._pack_args(args, kwargs)

        error_dict['data'] = arg_dict

        # Create RPC CALL
        json_dict = {}
        json_dict['jsonrpc'] = 2.0
        json_dict['error'] = error_dict
        json_dict['id'] = str(corr_id)

        return json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

    def _parseJSONRPC(self, message_body):

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
            raise InvaildParameterError(e.message, e.args)

        return method_name, args, kwargs, corr_id

    def _new_handle(self, prev_handle):
        return prev_handle

    def _process_incoming_message(self, routing_key, msg, sender=None, **params):
        json_msg = None

        if isinstance(msg, BrokerReturnMessage):
            json_dict = json.loads(msg.wrapped_message)
            if u"id" in json_dict:
                id = json_dict[u"id"]
                if msg.reply_code == 312:
                    if u"method" in json_dict:
                        json_msg = MethodNotFoundError(json_dict[u"method"], id=id, location="Broker")
                    else:
                        json_msg = CallerOfflineError(id=id)
        else:
            json_dict = json.loads(msg)

            if "result" in json_dict:

                json_msg = JsonRPCResult(result=json_dict["result"], id=json_dict["id"])

            elif "error" in json_dict:

                err_dict = json_dict['error']
                code = err_dict['code']
                message = err_dict['message']
                args, kwargs = self._unpack_args(err_dict['data'])

                self.logger.exception("Received an error result for call {0}".format(json_dict["id"]))
                error_constructor = ERRORS.get(code, JsonRPCError)
                json_msg = error_constructor(message, id=json_dict["id"], *args, **kwargs)

            elif "method" in json_dict:

                method_name, args, kwargs, corr_id = self._parseJSONRPC(msg)
                if corr_id is not None:
                    json_msg = JsonRPCCall(method=method_name, id=corr_id, args=args, kwargs=kwargs)
                else:
                    json_msg = JsonRPCNotify(method=method_name, args=args, kwargs=kwargs)

        return routing_key, json_msg, sender, params

    def _process_outgoing_message(self, routing_key, msg, **params):

        assert isinstance(msg, JsonRPCMessage)

        self.logger.debug("Sending Result: \n %s" % (msg))

        json_msg = None

        if isinstance(msg, JsonRPCCall):

            method, corr_id, args, kwargs = msg.get_as_tuple()
            if not corr_id:
                corr_id = str(uuid.uuid4())
            if not kwargs:
                kwargs = dict()
            if not args:
                args = list()

            json_msg = self._convert_to_JSONRPC(method, id=corr_id, args=args, kwargs=kwargs)

        elif isinstance(msg, JsonRPCNotify):

            method, corr_id, args, kwargs = msg.get_as_tuple()
            if not kwargs:
                kwargs = dict()
            if not args:
                args = list()

            json_msg = self._convert_to_JSONRPC(method, id=corr_id, args=args, kwargs=kwargs)

        elif isinstance(msg, JsonRPCResult):

            self.logger.debug("Sending Result: \n %s" % (msg))

            result, corr_id = msg.get_as_tuple()
            json_dict = {}
            json_dict['jsonrpc'] = 2.0
            json_dict['result'] = result
            json_dict['id'] = corr_id

            json_msg = json.dumps(json_dict, cls=self.jsonEncoder, check_circular=True)

        elif isinstance(msg, JsonRPCError):

            code, id, message, args, kwargs = msg.get_as_tuple()
            json_msg = self._convert_to_JSONRPC_Error(code, id, message, args, kwargs)

        else:
            self.logger.debug("Something strange happened.")

        params["content_type"] = u'application/json'
        if json_msg:
            return routing_key, json_msg, params
