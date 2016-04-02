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
from scenario import Scenario
from vnf import Vnf
from decaf_storage.utils import StdObject

__author__ = ''


class ScenarioVnf(Base, StdObject):

    public = Column(Boolean, default=False)

    scenario_id = Column(UUID(True), ForeignKey('scenarios.uuid'))
    scenario = relationship(Scenario, backref=backref('scenario_vnfs', uselist=True))

    vnf_id = Column(UUID(True), ForeignKey('vnfs.uuid'))
    vnf = relationship(Vnf, backref=backref('scenario_vnfs', uselist=True))

    graph = Column(String(250))

