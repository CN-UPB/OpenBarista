##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##
from time import sleep

from decaf_storage.database import Database
from decaf_storage.utils import calculate_tablename, generate_api_function_names, generate_function_names
from decaf_storage.json_base import StorageJSONEncoder

from decaf_storage.storage_adapter import StorageAdapter

from decaf_utils_components.base_daemon import daemonize
from decaf_utils_components.base_plugin import BasePlugin

import model

__author__ = ''
__date__ = "$27-okt-2015 12:45:41$"


class Storage(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(Storage, self).__init__(logger=logger, config=config)

        self.logger.debug('connect to database')
        self.db = Database(config["database"])
        self.logger.debug('pupulate database')
        self.db.init_db()
        self.logger.debug('connected to database')

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    def _after_connect(self):
        sleep(3)
        self.register_methods()

    def generate_call(self, call_type, cls):

        def storage_call(*args, **kwargs):
            storage_adapter = StorageAdapter(self.db, self.logger)
            return getattr(storage_adapter, call_type)(cls, *args, **kwargs)

        return storage_call

    def register_methods(self):
        """
        Registers the methods of the RPC component.
        :param:
        :return:
        """
        if self.rpc is not None:
            self.rpc.set_json_encoder(StorageJSONEncoder)

            self.logger.debug('Registering endpoints...')

            self.rpc.register('decaf_storage.version', self.version)
            self.rpc.register('decaf_storage.functions', self.functions)
            self.rpc.register('decaf_storage.contracts', self.contracts)

            funccount = 0
            """register functions for all database models"""
            for funcname, cls, call_type in generate_api_function_names(model):
                self.logger.debug('registering method %s' % funcname)
                funccount += 1
                self.rpc.register(funcname, self.generate_call(call_type, cls))

            self.logger.debug('%d Endpoints registered' % funccount)

    def deregister_methods(self):
        """
        Registers the methods of the RPC component.
        :param:
        :return:
        """

        if self.rpc is not None:
            self.logger.debug('Deregistering endpoints...')
            self.rpc.deregister('decaf_storage.version')
            self.rpc.deregister('decaf_storage.functions')
            self.rpc.deregister('decaf_storage.contracts')

            funccount = 0
            for funcname, cls, call_type in generate_api_function_names(model):
                funccount += 1
                self.logger.debug('deregistering method %s' % funcname)
                self.rpc.deregister(funcname)

            self.logger.debug('%d Endpoints deregistered' % funccount)

    def version(self):
        """
        Returns the component's version. This function implements the core.version contract and is required by the
        component manager, e.g. for heartbeat requests.
        :return:
        """
        return {'version': self.__version__,
                'date': "$27-okt-2015 12:45:41$"}

    @staticmethod
    def functions():
        """
        Gets a list of endpoints provided by this component. This function implements the core.functions contract and
        is required by the component manager.
        :return:
        """

        functions = [
            {
                'name': 'version',
                'contract': 'core.version'
            },
            {
                'name': 'functions',
                'contract': 'core.functions'
            },
            {
                'name': 'contracts',
                'contract': 'core.contracts'
            }
        ]
        for (cls, cls_name, call_type) in generate_function_names(model):
            functions.append({
                'name': '%s_%s' % (call_type, calculate_tablename(cls_name)),
                'contract': 'storage.%s_%s' % (call_type, calculate_tablename(cls_name))
            })

        return {'functions': functions}

    @staticmethod
    def contracts():
        """
        Gets a list of contracts provided by this component. This function implements the core.contracts contract and
        is required by the component manager.
        :return:
        """
        contracts = [{
                'name': 'core.version',
                'input': [],
                'output': [
                    {
                        'name': 'version',
                        'type': 'Version'
                    },
                    {
                        'name': 'date',
                        'type': 'DateTime'
                    },
                ]
            },
            {
                'name': 'core.functions',
                'input': [],
                'output': [
                    {
                        'name': 'functions',
                        'type': 'FunctionList'
                    }
                ]
            },
            {
                'name': 'core.contracts',
                'input': [],
                'output': [
                    {
                        'name': 'contracts',
                        'type': 'ContractList'
                    }
                ]
            }]

        for (cls, cls_name, call_type) in generate_function_names(model):
            contract = {'name': 'storage.%s_%s' % (call_type, calculate_tablename(cls_name))}
            if call_type == 'add':
                contract['input'] = [{
                    'name': 'data',
                    'type': '%sDictionary' % cls_name
                }]
                contract['output'] = [{
                    'name': 'integer',
                    'type': 'statusCode'
                }, {
                    'name': 'uuid',
                    'type': 'UUID'
                }]
            elif call_type == 'get':
                contract['input'] = [{
                    'name': 'options',
                    'type': 'QueryOptions'
                    }, {
                    'name': 'filters',
                    'type': 'QueryFilters'
                }]
                contract['output'] = [{
                    'name': 'integer',
                    'type': 'statusCode'
                }, {
                    'name': 'list',
                    'type': '%sList' % cls_name
                }]

            contracts.append(contract)

        return {'contracts': contracts}

    def dispose(self):

        if self.db is not None:
            self.db.dispose()
            self.db = None

def daemon():
    daemonize(Storage)

if __name__ == '__main__':
    daemon()
