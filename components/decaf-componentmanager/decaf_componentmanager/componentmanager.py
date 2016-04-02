##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_componentmanager.componentregistry import ComponentRegistry
from decaf_componentmanager.model.database import Database
from decaf_utils_components import BasePlugin, In


class ComponentManager(BasePlugin):

    def __init__(self, logger=None, config=None, *args, **kwargs):
        super(ComponentManager, self).__init__(logger=logger,config=config, **kwargs)
        self.config= config
        self.components = dict()

    def _after_connect(self):
        pass


    @In("name", unicode)
    @In("tenant", unicode)
    @In("exchange", unicode)
    @In("version", unicode)
    @In("functions", list)
    @In("contracts", list)
    @In("endpoints", list)
    def add(self, name=None, user=None, version=None, exchange=None, functions=None, contracts=None, endpoints=None):
        component = dict()
        component['name'] = name
        component['tenant'] = user
        # Get component version
        self.logger.debug("Get version of component %s" % name)

        component['version'] = version

        # Get component functions
        self.logger.debug("Get functions of component %s" % name)
        component['functions'] = functions
        component['contracts'] = contracts
        component['endpoints'] = endpoints

        self.logger.debug("Add component '%s' to the registry")
        # Add the component to the registr

        self.components.get(user, list()).append(component)
        return True



    @In("name", unicode)
    @In("tenant", unicode)
    @In("exchange", unicode)
    @In("version", unicode)
    @In("functions", list)
    @In("contracts", list)
    @In("endpoints", list)
    def update(self, exchange=None, functions=None, name=None, tenant=None, version=None, contracts=None, endpoints=None):




        component = None
        for component in self.components["user"]:

            component['version'] = version

            # Get component functions
            self.logger.debug("Get functions of component %s" % name)
            component['functions'] = functions
            component['contracts'] = contracts

            component['endpoints'] = endpoints

            self.logger.debug("Add component '%s' to the registry")
            # Add the component to the registry



            return True

        return False

    def on_unroutable_msg(self, routing_key, message, sender, **params):

        # TODO: Find out who did this

        # TODO: Check if there are rules, if not, add to rr-qeuee

        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        # Send again




    def _install_fallback(self, exchange):
        channel = self.rpc.get_transport_layer().get_rmq_control_channel()
        channel.queue_bind(self,self.queue, "#")

    def _install_rule(self, rule):
        """
        Configures RabbitMQ according to the given rule.
        :param rule:
        :return:
        """
        channel = self.rpc.get_transport_layer().get_rmq_control_channel()
        channel.queue_bind(rule["component"]["exchange"],rule["function"]["queue"], rule["routingkey"])
        pass


    def _assert_round_robin_queue(self, exchange, contract, key):
        channel = self.rpc.get_transport_layer().get_rmq_control_channel()
        channel.queue_create(name="RR_%s"%contract)
        channel.queue_bind(exchange,"RR_%s"%contract, key)