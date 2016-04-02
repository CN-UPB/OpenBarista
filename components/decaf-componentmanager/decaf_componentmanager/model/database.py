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

__author__ = 'Andreas Krakau'
__date__ = '$01-sep-2015 14:37:02$'

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()


class Database:
    def __init__(self, database=None):
        self.engine = None
        if database is not None:
            self.create_engine(database)

    def create_engine(self, database):
        if self.engine is None:
            if database['type'] == 'sqlite':
                if 'file' in database and len(database['file']) > 0:
                    db_url = 'sqlite:///%s' % database['file']
                else:
                    db_url = 'sqlite://'
            elif database['type'] in ['mysql', 'postgres']:
                db_url = '%s://%s:%s@%s:%s/%s' % (database['type'], database['user'], database['password'],
                                                  database['host'], database['port'], database['database'])

            self.engine = create_engine(db_url, convert_unicode=True)
            self.init_db()


    def create_session(self):
        return scoped_session(sessionmaker(autocommit=False,
                                           autoflush=False,
                                           bind=self.engine))

    def init_db(self):
        if self.engine is not None:
            Base.metadata.create_all(bind=self.engine)

    def __del__(self):
        self.dispose()

    def dispose(self):
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None
