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
from vm_instance import VmInstance

__author__ = 'tksarkar'


class VmInstanceKeypair(Base, StdObject):

    vm_instance_id = Column(UUID(True), ForeignKey('vm_instances.uuid'), nullable=False)
    vm_instance = relationship(VmInstance, backref=backref("vm_instance_keypairs", cascade="all, delete-orphan"))

    keypair_id = Column(INT, nullable=False)
    private_key = Column(String(2048))
    public_key = Column(String(2048))
    fingerprint = Column(String(256))
    username = Column(String(256))
    password = Column(String(256))
