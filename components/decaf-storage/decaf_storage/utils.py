##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import re

from sqlalchemy import Column, TIMESTAMP, func, text, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr

from decaf_storage.json_base import JsonEncodedDict

__author__ = ''


class TimestampMixin(object):
    created_at = Column(TIMESTAMP, default=func.now())
    modified_at = Column(TIMESTAMP, default=func.now())


class MetaMixin(object):
    meta = Column(JsonEncodedDict)


class HeaderMixin(object):
    @declared_attr
    def __tablename__(cls):
        return calculate_tablename(cls.__name__) + 's'

    @declared_attr
    def __table_args__(cls):
        return {'extend_existing': True}

    uuid = Column(postgresql.UUID(True), server_default=text("uuid_generate_v4()"), primary_key=True)
    name = Column(String(250), nullable=True)
    description = Column(String(450), nullable=True)


class StdObject(HeaderMixin, TimestampMixin, MetaMixin):

    def __repr__(self):
        return '%s (%s)\n\tname: %s\n\tdescription: %s\n\tcreated at: %s\n\tmodified at: %s' % (
            self.__class__.__name__,
            self.uuid,
            self.name,
            self.description,
            self.created_at,
            self.modified_at)


def calculate_tablename(name):
    """
    converts CamelCase to camel_case

    Example:
    calculate_tablename('HTTPResponseCodeXYZ')
    'http_response_code_xyz'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def generate_function_names(model):
    classes_dict = dict([(name, cls) for name, cls in model.__dict__.items() if isinstance(cls, type)])
    for cls_name, cls in classes_dict.iteritems():
        for call_type in ['add', 'get', 'delete', 'update']:
            yield (cls, cls_name, call_type)


def generate_api_function_names(model):
    """
    :return: all function names for the storage component
    derived from model classes
    """
    for (cls, cls_name, call_type) in generate_function_names(model):
        yield ('decaf_storage.%s_%s' % (call_type, calculate_tablename(cls_name)), cls, call_type)


def generate_functions(prefix, model):
    for (cls, cls_name, call_type) in generate_function_names(model):
        yield {
            'name': '%s_%s' % (call_type, calculate_tablename(cls_name)),
            'contract': '%s.%s_%s' % (prefix, call_type, calculate_tablename(cls_name))
        }
