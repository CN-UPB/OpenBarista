__author__ = "Andreas Krakau"
__date__ = "$15-sep-2015 10:37:22$"

import unittest

from decaf_componentmanager.model.database import Database
from decaf_componentmanager.model.component import Component
from decaf_componentmanager.model.contract import Contract
from decaf_componentmanager.model.port import Port
from decaf_componentmanager.model.contractinputport import ContractInputPort
from decaf_componentmanager.model.contractoutputport import ContractOutputPort



class DatabaseTests(unittest.TestCase):
    def test_create_component(self):
        config = {'type': 'sqlite'}
        db = Database(config)
        db.init_db()
        session = db.create_session()
        component = Component('testcomponent', 'bla')
        session.add(component)
        session.commit()
        self.assertEqual(component, session.query(Component).filter(Component.name == 'testcomponent').first())

    def test_create_contract(self):
        config = {'type': 'sqlite'}
        db = Database(config)
        db.init_db()
        session = db.create_session()
        contract = Contract('testcontract')
        input_port = Port('a', 'Boolean')
        output_port = Port('result', 'Boolean')
        input_port_link = ContractInputPort(contract=contract, port=input_port)
        output_port_link = ContractOutputPort(contract=contract, port=output_port)
        session.add(input_port_link)
        session.add(output_port_link)
        session.commit()
        self.assertEqual(contract, session.query(Contract).filter(Contract.name == 'testcontract').first())

# if __name__ == '__main__':
#     unittest.main()
