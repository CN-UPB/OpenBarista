##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *

from decaf_storage.database import Base
from scenario_net import ScenarioNet
from scenario_instance import ScenarioInstance
from decaf_storage.utils import StdObject

__author__ = ''


class ScenarioNetInstance(Base, StdObject):

    type = Column('type', ENUM('bridge', 'ptp', 'data', name='nettype'), default='data', nullable=False)

    scenario_net_id = Column(UUID(True), ForeignKey('scenario_nets.uuid'))
    scenario_net = relationship(ScenarioNet, backref=backref('scenario_net_instances', uselist=True))

    scenario_instance_id = Column(UUID(True), ForeignKey('scenario_instances.uuid'))
    scenario_instance = relationship(ScenarioInstance, backref=backref('scenario_net_instances', uselist=True))
