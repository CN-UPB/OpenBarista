##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from twisted.internet import defer
from decaf_utils_rpc.rpc_layer import RpcLayer
from . import __version__
from . import version_date

__author__ = "Andreas Krakau"
__date__ = "$08-sep-2015 11:40:09$"


class BunnyConnector(object):

    def __init__(self, url, component_registry, contract_registry, logger):
        self.logger = logger
        self.component_registry = component_registry
        self.contract_registry = contract_registry
        self._rpc = None
        self.rpc = RpcLayer(url, logger=logger)

    def version(self):
        return {'version': __version__,
                'date': version_date}


    def component_add(self, name, tenant):
        component = dict()
        component['name'] = name
        if not len(tenant):
            self.logger.exception('No component name specified')
            defer.returnValue({'result': False, 'error': {'message': 'No component name specified'}})
        self.logger.debug("Add component %s" % name)
        # Check tenant
        if not len(tenant):
            self.logger.exception("Could not add component '%s', because no tenant missing" % name)
            defer.returnValue({'result': False, 'error': {'message': 'No tenant specified'}})

        # Get component version
        self.logger.debug("Get version of component %s" % name)
        try:
            component['version'] = (yield self.rpc.call('%s.version' % component['name']))['version']
        except Exception as err:
            self.logger.exception("Could not get version of component '%s'" % name)
            defer.returnValue({'result': False, 'error': {'message': "Could not get version of component '%s'" % name}})

        # Get component functions
        self.logger.debug("Get functions of component %s" % name)
        try:
            component['functions'] = (yield self.rpc.call('%s.functions' % component['name']))['functions']
        except Exception as err:
            self.logger.exception("Could not get functions of component '%s'" % name)
            defer.returnValue(
                {'result': False, 'error': {'message': "Could not get functions of component '%s'" % name}})
        # Get component contracts and add them if there are unknown ones
        self.logger.debug("Get contracts of component %s" % name)
        try:
            component['contracts'] = (yield self.rpc.call('%s.contracts' % component['name']))['contracts']
        except Exception as err:
            self.logger.exception("Could not get contracts of component '%s'" % name)
            defer.returnValue(
                {'result': False, 'error': {'message': "Could not get contracts of component '%s'" % name}})

        self.logger.debug("Add component '%s' to the registry")
        # Add the component to the registry
        self.component_registry.add(component, tenant)
        defer.returnValue({'result': True})

    def component_remove(self, component_id):
        # Remove contracts that are only supported by this component
        self.component_registry.remove(component_id)

    def component_list(self):
        components = self.component_registry.get_list()
        result = []
        for component in components:
            result.append({'id': component.id,
                           'name': component.name})
        return {'result': result}

    def component_list_by_contract(self, contract_name):
        self.logger.debug("Retrieving functions for contract '%s'" % contract_name)
        contract = self.contract_registry[contract_name]
        self.logger.debug('Contract name: %s' % contract.name)
        result = []
        if contract is not None:
            component_name = None
            component = None
            self.logger.debug('Contract functions: %r %d' % (contract.functions, len(contract.functions)))
            for item in contract.functions:
                if component_name != item.component.name:
                    if component is not None:
                        result.append(component)
                    component_name = item.component.name
                    self.logger.debug('  Component name: %s' % item.component.name)
                    component = dict()
                    component['name'] = component_name
                    component['functions'] = []
                function = dict()
                function['name'] = item.name
                self.logger.debug('    Function name: %s' % item.name)
                component['functions'].append(function)
            if component is not None:
                result.append(component)

            # result = self.component_registry.get_functions_by_contract(contract)

        return {'result': result}

    def component_info(self, key):
        component = self.component_registry[key]

        result = {'id': component.id,
                  'name': component.name,
                  'functions': [],
                  }
        for function in component.functions:
            result['functions'].append({'name': function.name})
        return {'result': result}

    def contract_list(self):
        contracts = self.contract_registry.get_list()
        result = []
        for contract in contracts:
            item = {'name': contract.name, 'input': [], 'output': []}
            for port in contract.input_ports:
                item['input'].append({'name': port.name, 'type': port.data_type})
            for port in contract.output_ports:
                item['output'].append({'name': port.name, 'type': port.data_type})
            result.append(item)
        return {'result': result}

    def call(self, function, component=None, callback=None, function_args=[], function_kwargs={}, callback_args=[],
             callback_kwargs={}):
        rpc_name = function
        if component is not None:
            rpc_name = component + "." + rpc_name
        else:
            rpc_name = "*." + rpc_name

        d = self.rpc.call(rpc_name, *function_args, **function_kwargs)
        if callback is not None:
            d.addCallback(callback, *callback_args, **callback_kwargs)

    def __del__(self):
        self.dispose()

    def dispose(self):
        self.logger.debug('Closing rpc connection')
        if self.rpc is not None:
            self.deregister_rpc()
            self.rpc.dispose()
            self._rpc = None
