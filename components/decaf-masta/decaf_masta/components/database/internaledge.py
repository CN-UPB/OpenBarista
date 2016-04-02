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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import UUID

class InternalEdge(Base):
    __tablename__ = 'internal_edges'
    edge_id = Column(Integer, primary_key=True,autoincrement=True)
    cidr = Column(String(250), nullable=False)
    source_vm_instance = Column(UUID(True), nullable=False)
    source_os_port_id = Column(String(250), nullable=True)
    source_vm_ip = Column(String(250), nullable=True)
    source_interface_instance_id = Column(String(250), nullable=False)
    source_internal = Column(String(250), nullable=False)
    source_external = Column(String(250), nullable=False)
    source_physical_port = Column(String(250), nullable=False)
    target_vm_instance = Column(UUID(True), nullable=False)
    target_os_port_id = Column(String(250), nullable=True)
    target_vm_ip = Column(String(250), nullable=True)
    target_interface_instance_id = Column(String(250), nullable=False)
    target_internal = Column(String(250), nullable=False)
    target_external = Column(String(250), nullable=False)
    target_physical_port = Column(String(250), nullable=False)
    type = Column(String(250), nullable=False)
    network_os_id = Column(String(250))
    network_os_name = Column(String(250))
    subnetwork_os_id = Column(String(250))
    subnetwork_os_name = Column(String(250))
    datacenter_id = Column(Integer, ForeignKey('datacenters.datacenter_id'), nullable=False)
    scenario_instance_id = Column(UUID(True), ForeignKey('scenarios.scenario_instance_id'), nullable=False)