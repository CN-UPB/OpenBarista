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

from interface import Interface
from net_instance import NetInstance
from vm_instance import VmInstance
from decaf_storage.database import Base
from decaf_storage.utils import StdObject

__author__ = ''


class InterfaceInstance(Base, StdObject):

    internal_name = Column(String(36), nullable=False)
    external_name = Column(String(36), nullable=False)

    vm_instance_id = Column(UUID(True), ForeignKey('vm_instances.uuid'))
    vm_instance = relationship(VmInstance, backref=backref('interface_instances', uselist=True))

    net_instance_id = Column(UUID(True), ForeignKey('net_instances.uuid'))
    net_instance = relationship(NetInstance, backref=backref('interface_instances', uselist=True))

    interface_id = Column(UUID(True), ForeignKey('interfaces.uuid'))
    interface = relationship(Interface, backref=backref('interface_instances', uselist=True))

    type = Column('type', ENUM('bridge', 'ptp', 'data', 'mgmt', name='interfacetype'), default='data', nullable=False)

    vpci = Column(CHAR(12), nullable=False)
    bw = Column(INT, nullable=False)

    physical_name = Column(String(36))
    ip_address = Column(String(36))

