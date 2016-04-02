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
__date__ = '$01-sep-2015 14:16:48$'

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    input_ports = relationship('Port', secondary='contract_input_port')
    output_ports = relationship('Port', secondary='contract_output_port')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Contract %r>' % self.name
