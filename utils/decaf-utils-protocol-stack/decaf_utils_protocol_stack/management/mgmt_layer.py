##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import uuid

from decaf_utils_protocol_stack.management.management_messages import Update, Delete, Add
from decaf_utils_protocol_stack.protocol_layer import ProtocolLayer


class PluginMgmtLayer(ProtocolLayer):
    """

    """

    def __init__(self, next_layer, receive_func=None, logger=None, *args, **kwargs):
        """

        :param next_layer:
        :param receive_func:
        :param logger:
        :param args:
        :param kwargs:
        :return:
        """
        super(PluginMgmtLayer, self).__init__(next_layer, receive_func=receive_func, logger=logger, *args, **kwargs)

        add_msg = Add()
        corr_id = uuid.uuid4()

        self._next_layer.route("add", add_msg, corr_id=corr_id)

    def subscribe(self, routing_key, function_pointer, **params):
        # Normal subscribe
        super(PluginMgmtLayer, self).subscribe(routing_key, function_pointer, **params)

        # Register method with the manager
        mgmt = params.get("mgmt", dict())
        name = params.get("plugin_name", u"TARDIS")
        tenant = params.get("tenant_name", u"David Tenant")
        update_msg = Update(name, tenant, **mgmt)
        corr_id = uuid.uuid4()

        self._next_layer.route("update", update_msg, corr_id=corr_id)

    def _process_incoming_message(self, routing_key, msg, sender=None, **params):
        # Do nothing special
        return routing_key, msg, sender, params

    def _process_outgoing_message(self, routing_key, msg, **params):
        # Do nothing special
        return routing_key, msg, params
