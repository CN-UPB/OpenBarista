#!/usr/bin/env python

##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import decaf_storage
from decaf_utils_components import daemonize
from decaf_utils_components import BasePlugin, In, Out


class Placement(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(Placement, self).__init__(logger=logger, config=config)
        self.round_robin_init()

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    def _after_connect(self):
        self.s = decaf_storage.Endpoint(self.rpc, self.logger)

    @In('scenario_id', str)
    @Out('datacenter_mapping', dict)
    def place(self, scenario_id):
        """
        This method genrate a placement graph of the given scenario.

        :param scenario_id: of the scenario to place
        :return: a placement graph
        """
        self.logger.debug("RECEIVED placement request for scenario: %s" % scenario_id)
        datacenters = self.s.get('datacenter', options=[], filters={})

        if len(datacenters) == 0:
            raise Exception("There are not datacenters in the datacenter list.")

        # Use round robin. Woooah!
        datacenter = self.round_robin(datacenters)

        return datacenter

    def round_robin_init(self):
        """
        Initializes the round robin index.
        """

        self.round_robin_index = 0

    def round_robin(self, datacenters):
        """
        A simple round robin implementation.

        :param: A list of datacenters.
        :return: The index
        """

        n = len(datacenters)
        datacenter = datacenters[self.round_robin_index % n]
        self.round_robin_index = (self.round_robin_index + 1) % n
        return datacenter


def daemon():
    daemonize(Placement)

if __name__ == "__main__":
    daemon()
