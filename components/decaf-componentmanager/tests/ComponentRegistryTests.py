__author__ = "Andreas Krakau"
__date__ = "$22-sep-2015 14:24:22$"

import unittest
import logging

from decaf_componentmanager.model.database import Database
from decaf_componentmanager.model.component import Component
from decaf_componentmanager.model.function import Function
from decaf_componentmanager.model.contract import Contract
from decaf_componentmanager.componentregistry import ComponentRegistry


class ComponentRegistryTestCase(unittest.TestCase):
    @unittest.skip("skip component tests")
    def test_add(self):
        # Setup
        logger = logging.getLogger('ComponentManager')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)
        config = {'type': 'sqlite'}
        db = Database(config)
        db.init_db()
        session = db.create_session()
        contract = Contract('test.test_con')
        session.add(contract)
        session.commit()
        # Add the component to the registry
        registry = ComponentRegistry(db, logger)
        component_dict={'name': 'test_component',
                        'functions': [{
                            'name': 'test_func',
                            'contract': contract.name
                        }]}
        registry.add(component_dict, 0)
        # Check if everything is where it should be
        actual = session.query(Component).filter(Component.name == component_dict['name']).first()
        self.assertTrue(actual is not None, "Registry is unable to store component")
        self.assertTrue(len(actual.functions) > 0, "Registry is unable to store components function")
        actual_func = actual.functions[0]
        self.assertTrue(actual_func is not None, "Registry is unable to store components function")
        expected = 'test_func'
        self.assertEqual(expected, actual_func.name, "Registry is unable to store functions name")
        expected = contract
        self.assertEqual(expected, actual_func.contract, "Registry is unable to store functions contract")

    @unittest.skip("skip component tests")
    def test_remove(self):
        # Setup
        logger = logging.getLogger('ComponentManager')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)
        config = {'type': 'sqlite'}
        db = Database(config)
        db.init_db()
        session = db.create_session()
        contract = Contract('test.test_con')
        session.add(contract)
        component = Component("test_component", 0)
        function = Function("test_func", component, contract)
        session.add(function)
        session.add(component)
        session.commit()
        # Remove the component from the registry
        registry = ComponentRegistry(db, logger)
        registry.remove(component.name)

        actual = session.query(Function).filter(Function.name == function.name).first()
        self.assertTrue(actual is None, "Registry is unable to remove components function (%r)" % session.query(Function).all())
        actual = session.query(Component).filter(Component.name == component.name).first()
        self.assertTrue(actual is None, "Registry is unable to remove component")


    @unittest.skip("skip component tests")
    def test_request_heartbeat_from_component(self):
        pass

    @unittest.skip("skip component tests")
    def test_receive_heartbeat(self):
        pass

    @unittest.skip("skip component tests")
    def test_request_heartbeats(self):
        pass

    @unittest.skip("skip component tests")
    def test_get_list(self):
        # Setup
        logger = logging.getLogger('ComponentManager')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)
        config = {'type': 'sqlite'}
        db = Database(config)
        db.init_db()
        session = db.create_session()
        component1 = Component('testcomponent1', 'bla')
        component2 = Component('testcomponent2', 'blub')
        session.add(component1)
        session.add(component2)
        session.commit()
        registry = ComponentRegistry(db, logger)
        # There is only one component for tenant 'bla',
        expected = [component1]
        actual = registry.get_list('bla')
        self.assertEqual(expected, actual)
        # but two components over all
        expected = [component1, component2]
        actual = registry.get_list()
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
