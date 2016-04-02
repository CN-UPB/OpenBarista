##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from .model.rule import Rule
from .model.component import Component
from .model.function import Function

__author__ = "Andreas Krakau"
__date__ = "$19-jan-2016 14:04:10$"


class BunnyManager:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.logger.debug("Created BunnyManager")

    def rule_add(self, component_id, function_id, routing_key):
        """
        Adds a new rule.
        :param component_id: The component this rule belongs to.
        :param function_id: The function of an other component, which should be regulated.
        :param routing_key: The routing key the component uses to access a resource.
        :return:
        """
        self.logger.debug("Add rule (component_id=%d, function_id=%d, routing_key='%s')" % (component_id, function_id, routing_key))
        session = self.db.create_session()
        component = session.query(Component).filter(Component.id == component_id).one()
        function = session.query(Function).filter(Function.id == function_id).one()
        rule = Rule(component, function, routing_key)
        session.add(rule)
        session.commit()
        self.logger.debug("Add rule (component_id=%d, function_id=%d, routing_key='%s') => rule_id=%d" % (component_id, function_id, routing_key, rule.id))
        self._install_rule(rule)

    def rule_remove(self, rule_id):
        """
        Removes a rule.
        :param rule_id:
        :return:
        """
        self.logger.debug("Deleting rule %d..." % rule_id)
        session = self.db.create_session()
        rule = session.query(Rule).filter(Rule.id == rule_id).one()
        self._uninstall_rule(rule)
        session.delete(rule)
        session.commit()
        self.logger.debug("Deleted rule %d" % rule_id)

    def rule_remove(self, component, function, routing_key):
        """
        Removes a rule
        :param component:
        :param function:
        :param routing_key:
        :return:
        """
        session = self.db.create_session()
        rule = session.query(Rule).filter(Rule.component == component and Rule.function == function and Rule.routing_key == routing_key).first()
        if rule is not None:
            rule_id = rule.id
            self.logger.debug("Deleting rule %d..." % rule_id)
            self._uninstall_rule(rule)
            session.delete(rule)
            session.commit()
            self.logger.debug("Deleted rule %d" % rule_id)

    def rule_list(self):
        """
        Lists all rules.
        :return:
        """
        session = self.db.create_session()
        return session.query(Rule).all()

    def _install_rules(self):
        """
        Configures RabbitMQ to use the current rule set.
        :return:
        """
        pass

    def _uninstall_rules(self):
        """
        Configures RabbitMQ to use no rule set.
        :return:
        """
        pass

    def _install_rule(self, rule):
        """
        Configures RabbitMQ according to the given rule.
        :param rule:
        :return:
        """
        pass

    def _uninstall_rule(self, rule):
        """
        Removes the given rule from RabbitMQ's routing configuration.
        :param rule:
        :return:
        """
        pass