##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from .model.contract import Contract
from .model.port import Port
from .model.contractinputport import ContractInputPort
from .model.contractoutputport import ContractOutputPort

__author__ = "Andreas Krakau"
__date__ = "$27-aug-2015 11:40:09$"


class ContractRegistry:
    """
    A Contract describes a component function by giving an interface.

    This Registry manages the contract which are known by the componentmanager
    """

    def __init__(self, db, logger):
        """
        Creates a new contract registry
        :param db: The connector to the database
        :return:
        """
        self.db = db
        self.logger = logger
        self.logger.debug("Created ContractRegistry")

    def add(self, contract_dict, db_session=None):
        """
        Adds a new contract
        :param contract_dict:
        :return:
        """
        if db_session is None:
            session = self.db.create_session()
        else:
            session = db_session

        contract = Contract(contract_dict['name'])
        for item in contract_dict['input']:
            port = Port(item['name'], item['type'])
            link = ContractInputPort(contract=contract, port=port)
            session.add(link)

        for item in contract_dict['output']:
            port = Port(item['name'], item['type'])
            link = ContractOutputPort(contract=contract, port=port)
            session.add(link)

        session.add(contract)

        if db_session is None:
            session.commit()

    def remove(self, contract_id):
        """
        Removes a contract from the registry
        :param contract_id: The uuid of the contract
        :return:
        """
        session = self.db.create_session()
        contract = session.query(Contract).filter_by(id=contract_id).first()
        if contract is not None:
            # Todo Andreas: Remove ports
            self.logger.debug("Delete Contract %s" % contract.name)
            session.delete(contract)
            session.commit()

    def remove_unused(self):
        """
        Removes all contracts that are not referenced
        :return:
        """
        # Todo Andreas: Test ContractRegistry.remove_unused
        session = self.db.create_session()
        contracts = session.query(Contract).filter(Contract.functions.count() == 0).all()
        for item in contracts:
            session.delete(item)
        session.commit()

    def get_list(self):
        """
        Gets a list of all known contracts
        :return:
        """
        session = self.db.create_session()
        return session.query(Contract).all()

    def __getitem__(self, key):
        """
        Gets a contract by id
        :param key:
        :return:
        """
        session = self.db.create_session()
        if isinstance(key, (int, long)):
            return session.query(Contract).filter_by(id=key).first()
        else:
            return session.query(Contract).filter_by(name=key).first()
