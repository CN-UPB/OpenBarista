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

__author__ = "thgoette"  # Todo: Replace with your name
__date__ = "$22-sep-2015 22:05:41$"  # Todo: Replace with date

Base = declarative_base()


class Database:
    """

    """

    def __init__(self, database=None):
        self.session = None
        self.engine = None
        if database is not None:
            self.create_engine(database)

    def create_engine(self, database):
        """
        Creates a database connection.

        :param database: A dictionary containing data needed to connect to database.
        :return:
        """
        if self.engine is None:
            db_url = ''
            if database['type'] == 'sqlite':
                if 'file' in database and len(database['file']) > 0:
                    db_url = 'sqlite:///%s' % database['file']
                else:
                    db_url = 'sqlite://'
            elif database['type'] in ['mysql', 'postgres']:
                db_url = '%s://%s:%s@%s:%s/%s' % (database['type'], database['user'], database['password'],
                                                  database['host'], database['port'], database['database'])

            self.engine = create_engine(db_url, convert_unicode=True)

    def create_session(self):
        """
        Creates a database session.

        :return:
        """
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))

    def get_session(self):
        """
        Gets a database session.

        :return:
        """
        if self.session is None and self.engine is not None:
            self.create_session()
        return self.session

    def init_db(self):
        """
        Initializes the database schema.

        :return:
        """
        if self.engine is not None:
            Base.metadata.create_all(bind=self.engine)
