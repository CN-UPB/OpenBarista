##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from decaf_storage.database import Base
from decaf_storage.utils import StdObject
from interface_instance import InterfaceInstance
from scenario_interface import ScenarioInterface
from scenario_net_instance import ScenarioNetInstance
from vnf_instance import VnfInstance

__author__ = ''


class ScenarioInterfaceInstance(Base, StdObject):

    vnf_instance_id = Column(UUID(True), ForeignKey('vnf_instances.uuid'))
    vnf_instance = relationship(VnfInstance, backref=backref('scenario_interface_instances', uselist=True))

    scenario_net_instance_id = Column(UUID(True), ForeignKey('scenario_net_instances.uuid'))
    scenario_net_instance = relationship(ScenarioNetInstance, backref=backref('scenario_interface_instances', uselist=True))

    interface_instance_id = Column(UUID(True), ForeignKey('interface_instances.uuid'))
    interface_instance = relationship(InterfaceInstance, backref=backref('scenario_interface_instances', uselist=True))

    scenario_interface_id = Column(UUID(True), ForeignKey('scenario_interfaces.uuid'))
    scenario_interface = relationship(ScenarioInterface, backref=backref('scenario_interface_instances', uselist=True))
