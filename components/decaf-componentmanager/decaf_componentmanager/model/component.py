##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

__author__ = 'Andreas Krakau'
__date__ = '$01-sep-2015 14:15:27$'
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base
from .function import Function


class Component(Base):

    __tablename__ = 'component'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    tenant = Column(String(250), nullable=False)
    last_heartbeat = Column(DateTime)

    functions = relationship(Function, backref='component', cascade="all, delete-orphan")


    def __init__(self, name, tenant):
        self.name = name
        self.tenant = tenant
        self.last_heartbeat = None

    def __repr__(self):
        return '<Component %r>' % self.name
