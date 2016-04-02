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
__date__ = '$01-sep-2015 18:08:37$'

from sqlalchemy import Column, Integer, String
from .database import Base


class Port(Base):
    __tablename__ = 'port'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    data_type = Column(String(250), nullable=False)

    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type

    def __repr__(self):
        return '<Port %r %r>' % (self.name, self.data_type)
