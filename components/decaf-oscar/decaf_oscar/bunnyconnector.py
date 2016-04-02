from twisted.internet import defer
from decaf_utils_rpc.rpc_layer import RpcLayer
from . import __version__
from . import version_date

__author__ = "Andreas Krakau"
__date__ = "$20-oct-2015 12:22:23$"


class BunnyConnector(object):
    def __init__(self, url, logger):
        self.logger = logger
        self._rpc = None
        self.rpc = RpcLayer(url, logger=logger)

    @property
    def rpc(self):
        return self._rpc

    @rpc.setter
    def rpc(self, value):
        if self._rpc is not None:
            self.deregister_rpc()
        self._rpc = value
        if self._rpc is not None:
            self.register_rpc()

    def deregister_rpc(self):
        # deregister endpoints here
        self.logger.debug('Deregistering endpoints...')
        self.rpc.deregister('decaf_oscar.version')
        self.rpc.deregister('decaf_oscar.functions')
        self.rpc.deregister('decaf_oscar.contracts')
        self.rpc.deregister('decaf_oscar.scenario_start')
        self.logger.debug('Endpoints deregistered')

    def register_rpc(self):
        # register endpoints here
        self.logger.debug('Registering endpoints...')
        self.rpc.register('decaf_oscar.version', self.version)
        self.rpc.register('decaf_oscar.functions', self.functions)
        self.rpc.register('decaf_oscar.contracts', self.contracts)
        self.rpc.register('decaf_oscar.scenario_start', self.scenario_start)
        self.logger.debug('Endpoints registered')

    @rpc.setter
    def rpc(self, value):
        if self._rpc is not None:
            self.deregister_rpc()
        self._rpc = value
        if self._rpc is not None:
            self.register_rpc()

    def version(self):
        return {'version': __version__,
                'date': version_date}

    def functions(self):
        """
        Gets a list of endpoints provided by this component. This function implements the core.functions contract and
        is required by the component manager.

        :return:
        """
        return {'functions': [
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
            },
            {
                'name': 'scenario_start',
                'contract': 'oscar.deployment.scenario_start'
            }
        ]}

    def contracts(self):
        """
        Gets a list of contracts provided by this component. This function implements the core.contracts contract and
        is required by the component manager.

        :return:
        """
        return {'contracts': [
            {
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
            },
            {
                'name': 'oscar.deployment.scenario_start',
                'input': [
                    {
                        'name': 'scenario_id',
                        'type': 'UUID'
                    },
                    {
                        'name': 'scenario_instance_name',
                        'type': 'String'
                    },
                    {
                        'name': 'datacenter_id',
                        'type': 'UUID'
                    },
                    {
                        'name': 'startvms',
                        'type': 'Boolean'
                    }
                ],
                'output': [
                    {
                        'name': 'scenario_instance_id',
                        'type': 'UUID'
                    }
                ]
            }
        ]}

    @defer.inlineCallbacks
    def scenario_start(self, scenario_id, scenario_instance_name, datacenter_id, startvms):
        callees = []
        try:
            callees = (yield self.rpc.call('decaf_componentmanager.component_list_by_contract',
                                           contract_name="deployment.scenario_start"))
            self.logger.debug("Callees dump %r"%callees)
        except Exception as err:
            self.logger.exception("Could not resolve contract 'deployment.scenario_start'")
            defer.returnValue(
                {'scenario_instance_id': None, 'error': {'message': "Could not resolve contract 'deployment.scenario_start'"}})

        self.logger.debug("Has found callees: %r %r" % (isinstance(callees, list), len(callees) > 0))
        if isinstance(callees['result'], list) and len(callees['result'])>0:
            try:
                component = callees['result'][0]['name']
                function = callees['result'][0]['functions'][0]['name']
                self.logger.exception("Try to call '%s.%s'" % (component, function))
                result = (yield self.rpc.call('%s.%s'% (component, function), scenario_id, scenario_instance_name, datacenter_id, startvms))
                defer.returnValue(result)
            except Exception as err:
                self.logger.exception("Could not start scenario")
                defer.returnValue(
                    {'scenario_instance_id': None, 'error': {'message': "Could not start scenario"}})

    @defer.inlineCallbacks
    def call_contract(self, contract, callback=None, function_args=[], function_kwargs={}, callback_args=[],
                      callback_kwargs={}):
        callees = (yield self.rpc.call('decaf_componentmanager.component_list_by_contract', contract=contract))
        if isinstance(callees, list) and len(callees) > 0:
            self.call(callees[0]['functions'][0]['name'], callees[0]['name'], callback, function_args, function_kwargs,
                      callback_args, callback_kwargs)

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
