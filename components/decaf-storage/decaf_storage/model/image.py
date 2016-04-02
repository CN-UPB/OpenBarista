##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.orm import relationship
from sqlalchemy import *


from decaf_storage.database import Base
from datacenter import Datacenter
from decaf_storage.utils import StdObject

__author__ = ''


class Image(Base, StdObject):

    location = Column(String(200), nullable=False)
    datacenters = relationship(Datacenter, secondary='datacenter_images', backref='images')

    username = Column(String(200), nullable=True)
    password = Column(String(200), nullable=True)
