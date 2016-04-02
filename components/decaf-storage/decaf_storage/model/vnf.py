##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy import *

from decaf_storage.database import Base
from decaf_storage.utils import StdObject


__author__ = ''


class Vnf(Base, StdObject):

    path = Column(String(100))
    max_instance = Column(Integer)
    public = Column(Boolean, default=True)
    _class = Column(String(36), default='MISC')
