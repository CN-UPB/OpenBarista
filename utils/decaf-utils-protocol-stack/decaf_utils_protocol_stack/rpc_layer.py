##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

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

        The given function MUST return a result.

        Currently the rpc_name needs to be globally unique !!!

        :param rpc_name: A unique name for the rpc_layer method, e.g. <PluginName>.<MethodName>
        :param function_ptr: A function to be called. It has to return a result.
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

    def subscribe(self, tag, function_ptr, **params):
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
        Sets the encoder for dumping given return objects into json.

        :return:
        """
        pass
