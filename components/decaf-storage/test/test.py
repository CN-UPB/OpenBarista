#!/usr/bin/env python
import logging
import unittest

from decaf_storage.database import Database
import decaf_storage.model
from decaf_storage.storage import Storage
from decaf_storage.json_base import *
from decaf_storage.model.flavor import Flavor
from decaf_storage.model.image import Image
from decaf_storage.model.scenario import Scenario
from decaf_storage.model.scenario_vnf import ScenarioVnf
from decaf_storage.model.vm import Vm
from decaf_storage.model.vnf import Vnf
from decaf_storage.model.net import Net


class TestStorageAPI(unittest.TestCase):

    def setUp(self):
        db = Database({
            "type": 'postgresql',
            "host": 'localhost',
            "port": '5432',
            "database": 'decaf_storage',
            "user": 'decaf',
            "password": 'decafpw'
        })
        # db.drop_all()
        db.init_db()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.storage = Storage(db, logger=logger)

    def test_scenario_insert(self):
        # create VNF
        code, vnf_id = self.storage.add(Vnf, {
            'name': 'name',
            'description': 'description',
            'path': 'path',
            'public': False
        })
        print('VNF: ', vnf_id)
        self.assertTrue(code == 200)

        # create Image
        code, image_id = self.storage.add(Image,{
            'name': 'name',
            'description': 'description',
            'location': 'location'
        })
        print('Image: ', image_id)
        self.assertTrue(code == 200)
        # create Flavor

        code, flavor_id = self.storage.add(Flavor,{
            'name': 'name',
            'description': 'description',
            'disk': 12,
            'ram': 8,
            'vcpus': 4
        })
        print('Flavor: ', flavor_id)
        self.assertTrue(code == 200)

        # create VM
        code, vm_id = self.storage.add(Vm,{
            'name': 'name',
            'description': 'description',
            'vnf_id': vnf_id,
            'flavor_id': flavor_id,
            'image_id': image_id,
            'image_path': 'path'
        })
        print('VM: ', vm_id)
        self.assertTrue(code == 200)

        # create Scenario
        code, sce_id = self.storage.add(Scenario, {
            'name': 'name',
            'description': 'description'
        })
        print('Scenario: ', sce_id)
        self.assertTrue(code == 200)

        # add Vnf to Scenario
        code, scenario_vnf = self.storage.add(ScenarioVnf, {
            'name': 'name',
            'description': 'description',
            'scenario_id': sce_id,
            'vnf_id': vnf_id
        })
        print('Scenario VNF: ', scenario_vnf)
        self.assertTrue(code == 200)

        # add net to Scenario
        code, net_id = self.storage.add(Net, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'vnf_id': vnf_id
        })
        print('Net: ', net_id)
        self.assertTrue(code == 200)

        code, vnfs = self.storage.get(Vnf,
                                      filters={'vnf.uuid': vnf_id},
                                      options=['vms', 'scenario_vnfs.scenario'])
        self.assertTrue(code == 200)

        for vnf in vnfs:
            print(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
            vnf = json.loads(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
            print("VMS:\n", json.dumps(vnf['vms']))

if __name__ == '__main__':
    unittest.main()
