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
import re
import decimal
import datetime
from uuid import UUID
from json import JSONEncoder

from sqlalchemy.orm.state import InstanceState
from sqlalchemy import inspect
from sqlalchemy.ext import mutable
from sqlalchemy import String, TypeDecorator

__author__ = ''


class JsonEncodedDict(TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


mutable.MutableDict.associate_with(JsonEncodedDict)


class StorageJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, BaseException):
            return str(obj.message)
        elif hasattr(obj, '__json__'):
            return obj.__json__()

        return super(JSONEncoder, self).default(obj)


def get_entity_propnames(entity):
    ins = entity if isinstance(entity, InstanceState) else inspect(entity)
    return set(ins.mapper.column_attrs.keys() + ins.mapper.relationships.keys())


def get_entity_loaded_propnames(entity):
    """ Get entity property names that are loaded (e.g. won't produce new queries)"""
    ins = inspect(entity)
    keynames = get_entity_propnames(ins)

    # If the entity is not transient -- exclude unloaded keys
    # Transient entities won't load these anyway, so it's safe to include all columns and get defaults
    if not ins.transient:
        keynames -= ins.unloaded

    # If the entity is expired -- reload expired attributes as well
    # Expired attributes are usually unloaded as well!
    if ins.expired:
        keynames |= ins.expired_attributes

    return keynames


class JsonSerializableBase(object):
    """ Declarative Base mixin to allow objects serialization"""

    def __repr__(self):
        return '%s (%s)\n\tname: %s\n\tdescription: %s\n\tcreated at: %s\n\tmodified at: %s' % (
            self.__class__.__name__,
            self.uuid,
            self.name,
            self.description,
            self.created_at,
            self.modified_at)
    __json_private__ = set()

    def __json__(self):
        return {name: getattr(self, name)
                for name in get_entity_loaded_propnames(self) - self.__json_private__}
