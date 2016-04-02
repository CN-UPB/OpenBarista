##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import *

from decaf_storage.database import Base
from decaf_storage.utils import StdObject

__author__ = ''


class Datacenter(Base, StdObject):

    type = Column('type', ENUM('openstack', 'other', name='datacentertype'), default='openstack', nullable=False)

    datacenter_masta_id = Column(Integer, nullable=False)

    # vim_url = Column(UUID(True), nullable=False)
    # vim_url_admin = Column(String(100), nullable=False)

    # datacenter_vim_id = Column(String(100), nullable=False)

    # flavors = relationship('Flavor', secondary='datacenter_flavors', viewonly=True)
    # images = relationship('Image', secondary='datacenter_images', viewonly=True)

    def __repr__(self):
        return '<uuid: %s\n name: %s\n description: %s\n type: %s>' % \
               (self.uuid, self.name, self.description, self.type)
