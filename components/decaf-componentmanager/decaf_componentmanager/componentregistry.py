##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import datetime

from .model.component import Component
from .model.contract import Contract
from .model.function import Function

__author__ = "Andreas Krakau"
__date__ = "$27-aug-2015 01:15:32$"


class ComponentRegistry:
    def __init__(self, db, contract_registry, logger):
        self.db = db
        self.contract_registry = contract_registry
        self.logger = logger
        self.logger.debug('Created ComponentRegistry')
        self.time_out = 30

    def add(self, component_dict, tenant_id):
        """
        Adds a component to the registry
        :param component_dict:
        :param tenant_id:
        :return:
        """
        session = self.db.create_session()

        self.logger.debug("Check whether the given contracts for component '%s' are valid and store unknown ones" % component_dict['name'])
        for contract in component_dict['contracts']:
            self.contract_registry.add(contract, session)
        session.flush()
        component = Component(component_dict['name'], tenant_id)
        session.add(component)
        for func in component_dict['functions']:
            self.logger.debug("Find contract '%s' for function '%s'" % (func['contract'],func['name']))
            contract = session.query(Contract).filter(Contract.name == func['contract']).first()
            function = Function(func['name'], component, contract)
            session.add(function)

        session.commit()
        self.logger.debug("Created Component %s" % component.name)

    def remove(self, component_id=None, name=None):
        """
        Removes component from registry
        :param component_id:
        :param name:
        :return:
        """
        session = self.db.create_session()
        component = None
        if component_id is not None:
            component = session.query(Component).filter_by(id=component_id).first()
        elif name is not None:
            component = session.query(Component).filter_by(name=name).first()

        if component is not None:
            self.logger.debug("Delete functions of component %s" % component.name)
            for func in component.functions:
                session.delete(func)

            self.logger.debug("Delete Component %s" % component.name)
            session.delete(component)
            session.commit()

    def request_heartbeat_from_component(self, component, connector):
        """
        Calls a component for a heartbeat
        :param component:
        :param connector:
        :return:
        """
        connector.call("version",
                       component.name,
                       self.receive_heartbeat,
                       callback_kwargs={
                           'component_id': component.id,
                           'start_time': datetime.datetime.now()})

    def receive_heartbeat(self, component_id, start_time):
        """
        Callback for heartbeat
        :param component_id:
        :param start_time:
        :return:
        """
        end_time = datetime.datetime.now()
        if (end_time - start_time) < datetime.timedelta(0, self.time_out):
            session = self.db.create_session()
            component = session.query(Component).filter_by(id=component_id).first()
            component.last_heartbeat = start_time
            session.commit()

    def request_heartbeats(self, connector):
        """
        Calls all components for a heartbeat
        :param connector:
        :return:
        """
        for component in self.get_list():
            self.request_heartbeat_from_component(component, connector)

    def get_list(self, tenant_id=None):
        """
        Gets a list of all known components
        :return:
        """
        session = self.db.create_session()
        if tenant_id is not None:
            return session.query(Component).filter_by(tenant=tenant_id).all()
        else:
            return session.query(Component).all()

    def __getitem__(self, key):
        """
        Gets a component by id
        :param key:
        :return:
        """
        session = self.db.create_session()
        if isinstance(key, (int, long)):
            return session.query(Component).filter_by(id=key).first()
        else:
            return session.query(Component).filter_by(name=key).first()
