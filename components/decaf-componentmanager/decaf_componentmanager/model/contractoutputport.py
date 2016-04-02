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
__date__ = '$08-sep-2015 11:01:35$'

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref
from .database import Base
from .contract import Contract
from .port import Port


class ContractOutputPort(Base):
    __tablename__ = 'contract_output_port'
    contract_id = Column(Integer, ForeignKey('contract.id'), primary_key=True)
    port_id = Column(Integer, ForeignKey('port.id'), primary_key=True)
    port = relationship(Port, backref=backref('contract_output_port_assoc'))
    contract = relationship(Contract, backref=backref('output_port_assoc'))

    def __repr__(self):
        return '<ContractOutputPort %r->%r>' % (self.contract, self.port)
