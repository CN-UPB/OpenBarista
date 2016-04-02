##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__author__ = "Kristian Hinnenthal"
__date__ = "$12-okt-2015 22:05:41$"

Base = declarative_base()

class Database(object):
    """

    """

    def __init__(self, database=None):
        self.session = None
        self.engine = None
        if database is not None:
            self.create_engine(database)

    def create_engine(self, database):
        """
        Creates a database connection
        :param database: A dictionary containing data needed to connect to database
        :return:
        """
        if self.engine is None:
            db_url = ''
            if database['type'] == 'sqlite':
                if 'file' in database and len(database['file']) > 0:
                    db_url = 'sqlite:///%s' % database['file']
                else:
                    db_url = 'sqlite://'
            elif database['type'] in ['mysql', 'postgresql']:
                db_url = '%s://%s:%s@%s:%s/%s' % (database['type'], database['user'], database['password'],
                                                  database['host'], database['port'], database['database'])

            self.engine = create_engine(db_url, convert_unicode=True)

    def create_session(self):
        """
        Creates a database session
        :return:
        """
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))

    def get_session(self):
        """
        Gets a database session
        :return:
        """
        if self.session is None and self.engine is not None:
            self.create_session()
        return self.session

    def init_db(self):
        """
        Initializes the database schema
        :return:
        """
        if self.engine is not None:
            from decaf_masta.components import mastaagent
            from decaf_masta.components.database.datacenter import Datacenter
            from decaf_masta.components.database.flavor import Flavor
            from decaf_masta.components.database.image import Image
            from decaf_masta.components.database.keystone import Keystone
            from decaf_masta.components.database.vm_instance import VMInstance
            from decaf_masta.components.database.scenario import Scenario
            from decaf_masta.components.database.management_network import ManagementNetwork
            from decaf_masta.components.database.public_network import PublicNetwork
            from decaf_masta.components.database.monitoring_alarm import MonitoringAlarm
            from decaf_masta.components.database.management_network import ManagementNetwork
            from decaf_masta.components.database.internaledge import InternalEdge
            from decaf_masta.components.database.public_port import PublicPort
            from decaf_masta.components.database.keypair import KeyPair
            from decaf_masta.components.database.router import Router
            from decaf_masta.components.database.management_port import ManagementPort
            Base.metadata.create_all(bind=self.engine)

    def __del__(self):
        self.dispose()

    def dispose(self):
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None