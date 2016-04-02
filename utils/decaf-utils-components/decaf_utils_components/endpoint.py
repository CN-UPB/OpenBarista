##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##


from meta_classes import _make_function_typesafe


class Endpoint(object):
    """

    """

    DEFAULT_TIMEOUT = 10

    def __init__(self, BasePlugin, rpc=None, logger=None):
        self.logger = logger
        self.rpc = rpc
        self.plugin_class = BasePlugin
        self.routing_key = BasePlugin.__name_camel_case__()
        self.timeout = self.DEFAULT_TIMEOUT
        # TODO: UPDATE

        pass


    def set_timeout(self, timeout):
        self.timeout = timeout


    def __getattr__(self, item):
        if hasattr(self.plugin_class, item):
            plugin_fct = self.plugin_class.__dict__[item]
            return _make_function_typesafe(self.__call_on_rpc__(plugin_fct), plugin_fct.__dict__["contract"])
        else:
            self.logger.error("Trying to call nonexistent method")
            raise BaseException("Endpoint for %s doesn't have method %s" % self.plugin_class, item)

    def __call_on_rpc__(self, method):

        def call(*args, **kwargs):
            try:
                rpc_name = "%s.%s" % (self.routing_key, method.func_name)
                self.logger.info("Calling method {0}".format(rpc_name))
                return self.rpc.callSync(self.timeout, rpc_name, *args, **kwargs)
            except BaseException as e:
                self.logger.error("Error while calling method with (%s) and {%s}"% (args,kwargs))
                self.logger.error("Exception was : \n %s" %e)
                raise e

        call.func_name = method.func_name
        call.func_dict = method.func_dict
        return call