##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, backref
from .database import Base
from .component import Component
from .function import Function

__author__ = 'Andreas Krakau'
__date__ = '$19-jan-2016 13:57:42$'


class Rule(Base):

    __tablename__ = 'rule'


    id = Column(Integer, primary_key=True)
    component_id = Column(Integer, ForeignKey('component.id'))
    component = relationship(Component, backref=backref('rules'))
    function_id = Column(Integer, ForeignKey('function.id'))
    function = relationship(Function, backref=backref('rules'))
    routing_key = Column(String(250), nullable=False)
    is_black = Column(Boolean, default=True)

    def __init__(self, component, function, routing_key):
        self.component = component
        self.function = function
        self.routing_key = routing_key

    def __repr__(self):
        return '<Rule %r>' % self.name
