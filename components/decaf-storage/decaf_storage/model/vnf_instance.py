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
from datacenter import Datacenter
from scenario_instance import ScenarioInstance
from vnf import Vnf
from decaf_storage.utils import StdObject

__author__ = ''


class VnfInstance(Base, StdObject):

    scenario_instance_id = Column(UUID(True), ForeignKey('scenario_instances.uuid'), nullable=False)
    scenario_instance = relationship(ScenarioInstance, backref=backref("vnf_instances", cascade="all, delete-orphan"))

    vnf_id = Column(UUID(True), ForeignKey('vnfs.uuid'), nullable=False)
    vnf = relationship(Vnf, backref=backref("vnf_instances", cascade="all, delete-orphan"))

    datacenter_id = Column(UUID(True), ForeignKey('datacenters.uuid'), nullable=False)
    datacenter = relationship(Datacenter, backref=backref("vnf_instances", cascade="all, delete-orphan"))

