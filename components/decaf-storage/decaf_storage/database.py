##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from json_base import JsonSerializableBase

Base = declarative_base(cls=(JsonSerializableBase,))


__author__ = ""
__date__ = "$27-okt-2015 12:45:41$"


class Database:
    """
    Use postgrsql with contrib package and psycopg2 driver!
    afterwards enable
    \c yourdatabas
    CREATE EXTENSION "uuid-ossp";
    """

    def __init__(self, database=None):
        self.session = None
        self.engine = None
        if database is not None:
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
                self.engine = create_engine(db_url, connect_args={'client_encoding': 'utf8'})

    def create_session(self):
        """
        Creates a database session
        :return:
        """
        return scoped_session(sessionmaker(autocommit=False,
                                           autoflush=False,
                                           bind=self.engine))

    def init_db(self):
        """
        Initializes the database schema
        :return:
        """
        if self.engine is not None:
            Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        return Base.metadata.drop_all(bind=self.engine)
        # return
        # Base.metadata.reflect(bind=self.engine)
        # for table in reversed(Base.metadata.sorted_tables):
        #     table.drop(self.engine)

    def __del__(self):
        self.dispose()

    def dispose(self):
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
