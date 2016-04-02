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
from decaf_storage.utils import StdObject
from vnf_instance import VnfInstance
from vm import Vm

__author__ = ''


class VmInstance(Base, StdObject):

    vnf_instance_id = Column(UUID(True), ForeignKey('vnf_instances.uuid'), nullable=False)
    vnf_instance = relationship(VnfInstance, backref=backref("vm_instances", cascade="all, delete-orphan"))

    vm_id = Column(UUID(True), ForeignKey('vms.uuid'), nullable=False)
    vm = relationship(Vm, backref=backref("vm_instances", cascade="all, delete-orphan"))