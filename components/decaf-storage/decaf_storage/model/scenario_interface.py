##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *

from decaf_storage.database import Base
from interface import Interface
from scenario_net import ScenarioNet
from scenario_vnf import ScenarioVnf
from decaf_storage.utils import StdObject

__author__ = 'sdjoum'


class ScenarioInterface(Base, StdObject):

    scenario_vnf_id = Column(UUID(True), ForeignKey('scenario_vnfs.uuid'))
    scenario_vnf = relationship(ScenarioVnf, backref=backref('scenario_interfaces', uselist=True))

    scenario_net_id = Column(UUID(True), ForeignKey('scenario_nets.uuid'))
    scenario_net = relationship(ScenarioNet, backref=backref('scenario_interfaces', uselist=True))

    interface_id = Column(UUID(True), ForeignKey('interfaces.uuid'))
    interface = relationship(Interface, backref=backref('scenario_interfaces', uselist=True))

    public = Column(Boolean, nullable=False)