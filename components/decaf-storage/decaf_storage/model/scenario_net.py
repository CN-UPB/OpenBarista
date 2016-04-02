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
from scenario import Scenario
from decaf_storage.utils import StdObject

__author__ = 'sdjoum'


class ScenarioNet(Base, StdObject):

    type = Column('type', ENUM('bridge', 'ptp', 'data', name='nettype'), default='data', nullable=False)

    scenario_id = Column(UUID(True), ForeignKey('scenarios.uuid'))
    scenario = relationship(Scenario, backref=backref('scenario_nets', uselist=True))
