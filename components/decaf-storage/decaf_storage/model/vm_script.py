##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.dialects.postgresql import UUID,BYTEA
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *

from decaf_storage.database import Base
from vm import Vnf
from decaf_storage.utils import StdObject

class VmScript(Base,StdObject):
    """
    A generic file, e.g. a bash script, that shall be transferred to the VM on startup.
    """

    # The script as Bytearray
    script = Column(BYTEA)

    name = Column(String(256), nullable=False)

    vnf_id = Column(UUID(True), ForeignKey('vnfs.uuid'), nullable=False)
    vnf = relationship(Vnf, backref=backref("vm_scripts", cascade="all, delete-orphan"))