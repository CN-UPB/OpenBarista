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
import json

class Keystone(Base):
    __tablename__ = 'keystone_credentials'
    keystone_id = Column(Integer, primary_key=True,autoincrement=True)
    keystone_url = Column(String(250), nullable=False)
    keystone_domain_id = Column(String(250), nullable=False)
    keystone_domain_name = Column(String(250), nullable=False)
    keystone_project_name = Column(String(250), nullable=False)
    keystone_user = Column(String(250), nullable=False)
    keystone_pass = Column(String(250), nullable=False)
    datacenters = relationship('Datacenter',backref='keystone_credentials')

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return_dict = {
            "keystone_credentials" : {
                "keystone_id" : self.keystone_id,
                "keystone_url" : self.keystone_url,
                "keystone_domain_id": self.keystone_domain_id,
                "keystone_domain_name": self.keystone_domain_name,
                "keystone_project_name": self.keystone_project_name,
                "keystone_user" : self.keystone_user,
                "keystone_pass" : self.keystone_pass,
            }
        }

        return return_dict