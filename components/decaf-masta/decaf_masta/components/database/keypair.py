##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

__author__ = 'Kristian Hinnenthal'
__date__ = '$07-jan-16$'
from sqlalchemy import Column, Integer, String, ForeignKey
from .mastadatabase import Base
from sqlalchemy.dialects.postgresql import UUID

class KeyPair(Base):
    __tablename__ = 'keypairs'
    keypair_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    vm_instance_id = Column(UUID(True), nullable=False)
    datacenter_id = Column(Integer, ForeignKey('datacenters.datacenter_id'), nullable=False)