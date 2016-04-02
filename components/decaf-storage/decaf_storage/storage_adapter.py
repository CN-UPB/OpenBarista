#!/usr/bin/env python

##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import json
import sys

from sqlalchemy.exc import DBAPIError, StatementError
from sqlalchemy.orm import contains_eager

from decaf_storage.json_base import StorageJSONEncoder

import model

__author__ = ''
__date__ = "$27-okt-2015 12:45:41$"

# following points are priority sorted
# TODO: include lazyloading e.g. 'joined' attributes
# TODO: ORM-level delete cascade vs. FOREIGN KEY level ON DELETE cascade


class StorageAdapter(object):
    __version__ = "0.1-dev01"

    def __init__(self, db=None, logger=None):

        self.logger = logger
        self.db = db

        self.logger.debug("instantiate new StorageAdapter")
        self.s = self.db.create_session()
        self.currentClass = None

    def add(self, classname, data):
        """ adds an object with a given class into the DB in a generic way
        :param classname: the classname of the object to be added
        :param data: the data dictionary with the data to be inserted
        :return: the uuid of the newly created object
        """
        try:
            obj = classname(**data)
            self.s.add(obj)
            self.s.commit()
        except DBAPIError as e:
            self.logger.exception("Error in Statement :\n%s\n %s" % (e.statement, e.orig))
            return 500, ("Error in Statement :\n%s\n %s" % (e.statement, e.orig))
        except StatementError as e:
            self.logger.exception(e)
            return 500, ("Unexpected error:%s: %s\nStacktrace:\n%s" % sys.exc_info())
        else:
            self.logger.debug("return uuid %s" % str(obj.uuid))
            return 200, str(obj.uuid)

    def get(self, classname, options, filters):
        """ gets the object which maches the specified filters and loads nested objects given in object
        :param classname:
        :param options:
        :param filters:
        :return:
        """
        if not options:
            options = []

        if not filters:
            filters = {}
        try:
            # TODO: bad codestyle!
            self.currentClass = classname
            self.logger.debug('received get querry for %s\n options %s\n filter: %s' %
                              (classname, options, filters))
            q = self.__query_builder(self.s.query(classname), options, filters)
            self.logger.debug(q)
            result = q.all()
        except DBAPIError as e:
            self.logger.exception("DBAPIError in Statement:\n%s\n %s" % (e.statement, e.orig))
            return 500, "DBAPIError in Statement:\n{0}\n {1}".format(e.statement, e.orig)
        except StatementError as e:
            self.logger.exception(e)
            return 500, "StatementError:\n{0}: {1}\nStacktrace:\n{2}".format(sys.exc_info())
        except Exception as e:
            self.logger.exception(e)
            return 500, "Unexpected error:\n{0}: {1}\nStacktrace:\n{2}".format(sys.exc_info())
        else:
            self.logger.debug('return resultset \n' + json.dumps(result, cls=StorageJSONEncoder, check_circular=True))
            return 200, result

    def update(self, classname, uuid, data):
        try:
            result = self.s.query(classname).filter(getattr(classname, 'uuid') == uuid).update(data)
            self.s.commit()
        except DBAPIError as e:
            self.logger.exception("DBAPIError in Statement:\n%s\n %s" % (e.statement, e.orig))
            return 500, ("DBAPIError in Statement:\n%s\n %s" % (e.statement, e.orig))
        except StatementError as e:
            self.logger.exception(e)
            return 500, ("StatementError:\n%s: %s\nStacktrace:\n%s" % sys.exc_info())
        except Exception as e:
            self.logger.exception(e)
            return 500, ("Unexpected error:\n%s: %s\nStacktrace:\n%s" % sys.exc_info())
        else:
            self.logger.debug('return resultset \n%s' % json.dumps(result, cls=StorageJSONEncoder, check_circular=True))
            return 200, result

    def delete(self, classname, uuid):
        obj = self.s.query(classname).filter_by(uuid=uuid).first()
        self.s.delete(obj)
        self.s.commit()
        return 200, True

    def __query_builder(self, q, options, filters):
        """Add options for eagger loading and filter on top of a give query q.
        :param q:
        :param options: list of strings for eagger loading
        :param filters: mapping of filters
        :return:
        """
        return self.__query_filter_builder(
            self.__query_option_builder(
                self.__query_join_builder(
                    q,
                    options),
                options
            ),
            filters
        )

    def __query_filter_builder(self, q, filters):
        if not filters:
            filters = {}

        if len(filters) > 0:
            fltr, value = filters.popitem()
            myfilter = self.__build_filter(fltr)
            return self.__query_filter_builder(q, filters)\
                .filter(myfilter == value)
        else:
            return q

    def __build_filter(self, fltr):
        fltr_list = fltr.split('.')
        if len(fltr_list) > 1:
            c = getattr(model, fltr_list[0].title())
            return getattr(c, fltr_list[1])
        else:
            return getattr(self.currentClass, fltr)

    def __query_join_builder(self, q, paths):
        if len(paths) > 0:
            joins = paths[-1].split('.')
            return self.__query_join_builder(q, paths[:-1])\
                .join(*joins)
        else:
            return q

    def __query_option_builder(self, q, paths):
        if len(paths) > 0:
            return self.__query_option_builder(q, paths[:-1])\
                .options(self.__query_joinedload_builder(paths[-1].split('.')))
        else:
            return q

    def __query_joinedload_builder(self, path):
        if len(path) > 1:
            return self.__query_joinedload_builder(path[:-1]).contains_eager(path[-1])
        else:
            return contains_eager(path[-1])

    def __del__(self):
        self.dispose()

    def dispose(self):
        if self.s is not None:
            self.s.close()
