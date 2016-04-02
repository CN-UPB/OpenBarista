##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.dialects.postgresql import UUID,JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *

from decaf_storage.database import Base
from decaf_storage.json_base import JsonEncodedDict
from flavor import Flavor
from image import Image
from vnf import Vnf
from decaf_storage.utils import StdObject

__author__ = ''


class Vm(Base, StdObject):
    vnf_id = Column(UUID(True), ForeignKey('vnfs.uuid'))
    vnf = relationship(Vnf, backref=backref('vms', uselist=True))

    # The maximal number instances
    max_instance = Column(Integer)

    # The events, this virtual machine supports
    events = Column(JsonEncodedDict)

    # A list of (URLs to) files, which need to be transferred to the VM
    files = Column(JsonEncodedDict)

    # The filepath were all the script are stored
    script_path = Column(String(200), default="/tmp/decaf-vnf-manager/")

    flavor_id = Column(UUID(True), ForeignKey('flavors.uuid'))
    flavor = relationship(Flavor, backref=backref('vms', uselist=True))

    image_id = Column(UUID(True), ForeignKey('images.uuid'))
    image = relationship(Image, backref=backref('vms', uselist=True))
    image_path = Column(String(250), nullable=False)

    # nfvo_tenant_id = Column(UUID(True), ForeignKey('nfvo_tenants.uuid'))
    # nfvo_tenant = relationship('NFVOTenant', backref=backref('vms', uselist=True))
