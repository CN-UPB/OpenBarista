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
from .keystone import Keystone
import json

class Datacenter(Base):
    __tablename__ = 'datacenters'
    datacenter_id = Column(Integer, primary_key=True,autoincrement=True)
    datacenter_name = Column(String(250), nullable=False)
    keystone_id = Column(Integer, ForeignKey('keystone_credentials.keystone_id'), nullable=False)
    keystone_region = Column(String(250), nullable=False)
    flavors = relationship('Flavor', backref='datacenters')
    images = relationship('Image', backref='datacenters')
    monitoring_alarms = relationship('MonitoringAlarm', backref='datacenters')
    management_networks = relationship('ManagementNetwork', backref='datacenters')
    public_networks = relationship('PublicNetwork', backref='datacenters')
    vm_instances = relationship('VMInstance', backref='datacenters')
    internal_edges = relationship('InternalEdge', backref='datacenters')
    public_ports = relationship('PublicPort', backref='datacenters')
    keypairs = relationship('KeyPair', backref='datacenter')

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return_dict = {
            "datacenter" : {
                "datacenter_id": self.datacenter_id,
                "datacenter_name": self.datacenter_name,
                "keystone_id": self.keystone_id,
                "keystone_region": self.keystone_region
            }
        }
        return return_dict