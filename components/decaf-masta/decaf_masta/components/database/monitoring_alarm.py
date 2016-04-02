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
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .mastadatabase import Base
from .datacenter import Datacenter
from sqlalchemy.dialects.postgresql import UUID

class MonitoringAlarm(Base):
    __tablename__ = 'monitoring_alarms'
    monitoring_alarm_id = Column(Integer, primary_key=True, autoincrement=True)
    datacenter_id = Column(Integer, ForeignKey('datacenters.datacenter_id'), nullable=False)
    alarm_os_id = Column(String(250), nullable=False)
    type=Column(String(250), nullable=False)
    vm_instance_id=Column(UUID(True), nullable=False)
    comparison_operator=Column(String(250), nullable=False)
    threshold=Column(Float, nullable=False)
    threshold_type=Column(String(250), nullable=False)
    statistic=Column(String(250), nullable=False)
    period=Column(Integer, nullable=False)
