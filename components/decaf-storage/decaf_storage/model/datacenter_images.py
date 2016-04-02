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
from sqlalchemy.orm import relationship
from sqlalchemy import *


from decaf_storage.database import Base
from datacenter import Datacenter
from image import Image
from decaf_storage.utils import StdObject

__author__ = ''


class DatacenterImage(Base, StdObject):

    masta_image_id = Column(INTEGER, nullable=False)

    image_id = Column(UUID(True), ForeignKey('images.uuid'), primary_key=True)
    image = relationship(Image)

    datacenter_id = Column(UUID(True), ForeignKey('datacenters.uuid'), primary_key=True)
    datacenter = relationship(Datacenter)
