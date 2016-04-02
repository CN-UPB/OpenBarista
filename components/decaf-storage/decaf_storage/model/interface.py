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
from net import Net

from vm import Vm
from decaf_storage.database import Base
from decaf_storage.utils import StdObject

__author__ = ''


class Interface(Base, StdObject):

    internal_name = Column(String(36), nullable=False)
    external_name = Column(String(36), nullable=False)

    vm_id = Column(UUID(True), ForeignKey('vms.uuid'))
    vm = relationship(Vm, backref=backref('interfaces', uselist=True))

    net_id = Column(UUID(True), ForeignKey('nets.uuid'))
    net = relationship(Net, backref=backref('interfaces', uselist=True))

    type = Column('type', ENUM('bridge', 'ptp', 'data', 'mgmt', name='interfacetype'), default='data', nullable=False)

    vpci = Column(CHAR(12), nullable=False)
    bw = Column(INT, nullable=False)