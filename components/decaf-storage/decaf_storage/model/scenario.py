##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy import *

from decaf_storage.database import Base
from decaf_storage.utils import StdObject

__author__ = ''


class Scenario(Base, StdObject):
    public = Column(Boolean, default=False)

    # nfvo_tenant_id = Column(UUID(True), ForeignKey('nfvo_tenants.uuid'))
    # nfvo_tenant = relationship(NFVOTenant, backref=backref('scenarios', uselist=True))

    # datacenter_id = Column(UUID(True), nullable=False)
