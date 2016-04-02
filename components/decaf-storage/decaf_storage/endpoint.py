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


class Endpoint:
    """
        This class encapsulates storage calls from other components.
        It tries to simplify and to improve readability of all components
        that are making execive use of storage component.
    """
    def __init__(self, rpc, logger):
        self.logger = logger
        self.rpc = rpc

    def get(self, object_name, *args, **kwargs):
        function = 'decaf_storage.get_' + object_name
        result, object_list = self.rpc.callSync(30, function, *args, **kwargs)

        if result != 200:
            self.logger.error(object_name + " selection failed")
            raise BaseException(object_name + " selection failed")

        self.logger.debug("STORAGE GET: %s\n%s" % (object_name.upper(), json.dumps(object_list, indent=4)))
        return object_list

    def add(self, object_name, *args, **kwargs):
        function = 'decaf_storage.add_' + object_name
        result, uuid = self.rpc.callSync(10, function, *args, **kwargs)

        if result != 200:
            self.logger.error(object_name + " instance insertion failed")
            raise BaseException(object_name + " instance insertion failed")

        self.logger.debug("STORAGE INSERT: %s\n%s" % (object_name.upper(), json.dumps(uuid, indent=4)))
        return uuid

    def update(self, object_name, *args, **kwargs):
        function = 'decaf_storage.update_' + object_name
        result, uuid = self.rpc.callSync(10, function, *args, **kwargs)

        if result != 200:
            self.logger.error(object_name + " instance update failed")
            raise BaseException(object_name + " instance update failed")

        filter_arg = ""
        for name, value in kwargs.items():
            filter_arg += '{0} = {1}'.format(name, value)
        self.logger.debug("STORAGE UPDATE: %s by\n%s" % (object_name.upper(), filter_arg))
        return uuid

    def delete(self, object_name, *args, **kwargs):
        function = 'decaf_storage.delete_' + object_name
        result, scenario_instance_id = self.rpc.callSync(10, function, *args, **kwargs)

        if result != 200:
            self.logger.error(object_name + " instance deletion failed")
            raise BaseException(object_name + " instance deletion failed")

        filter_arg = ""
        for name, value in kwargs.items():
            filter_arg += '{0} = {1}'.format(name, value)
        self.logger.debug("STORAGE DELETE: %s by\n%s" % (object_name.upper(), filter_arg))
