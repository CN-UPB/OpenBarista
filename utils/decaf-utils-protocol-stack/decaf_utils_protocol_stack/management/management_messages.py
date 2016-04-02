##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_utils_protocol_stack.json import JsonRPCCall


class ManagementMessage(JsonRPCCall):
    pass


class Update(ManagementMessage):
    def __init__(self, name, tenant, **kwargs):
        super(Update, self).__init__(method="update", kwargs={
            "name": name,
            "tenant": tenant,
        }.update(kwargs))


class Add(ManagementMessage):
    def __init__(self, name=None, tenant=None, version=None, exchange=None, contracts=None, functions=None,
                 endpoints=None):
        super(Add, self).__init__(method="add", kwargs={
            "name": name,
            "tenant": tenant,
            "version": version,
            "exchange": exchange,
            "contracts": contracts,
            "functions": functions,
            "endpoints": endpoints
        })


class Delete(ManagementMessage):
    def __init__(self, name, tenant):
        super(Delete, self).__init__(method="delete", kwargs={
            "name": name,
            "tenant": tenant,
        })
