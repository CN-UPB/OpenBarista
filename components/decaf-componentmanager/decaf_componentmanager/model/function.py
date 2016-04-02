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
__date__ = '$01-sep-2015 18:09:48$'

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref
from .contract import Contract
from .database import Base


class Function(Base):
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    component_id = Column(Integer, ForeignKey('component.id'))
    contract_id = Column(Integer, ForeignKey('contract.id'))
    contract = relationship(Contract, backref=backref('functions')) # , order_by='Function.component_id'
    queue = Column(String(250), nullable=False)

    def __init__(self, name, component, contract, queue):
        self.name = name
        self.queue = queue
        component.functions.append(self)
        contract.functions.append(self)

    def __repr__(self):
        return '<Function %r>' % self.name
