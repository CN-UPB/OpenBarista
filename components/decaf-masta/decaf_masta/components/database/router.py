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
__date__ = '$13-okt-2015 14:15:27$'
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .mastadatabase import Base
from .datacenter import Datacenter

class Router(Base):
    __tablename__ = 'routers'
    router_id = Column(Integer, primary_key=True, autoincrement=True)
    router_os_id = Column(String(250))
    router_os_name = Column(String(250))
    datacenter_id = Column(Integer, ForeignKey('datacenters.datacenter_id'), nullable=False)