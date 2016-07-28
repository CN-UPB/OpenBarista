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

from model.database import Database
from model.scenario import Scenario
from storage import Storage
import json
from decaf_storage.json_base import StorageJSONEncoder
import logging
from decaf_storage.model.flavor import Flavor
from decaf_storage.model.image import Image
from decaf_storage.model.scenario import Scenario
from decaf_storage.model.scenario_vnf import ScenarioVnf
from decaf_storage.model.vm import Vm
from decaf_storage.model.vnf import Vnf

LOGFILE = '/var/log/decaf/loaddata.log'

#class TestStorageAPI(unittest.TestCase):
class TestStorageAPI():

   def __init__(self):
       db = Database({
           "type": 'postgresql',
           "host": 'fg-cn-sandman1.cs.upb.de',
           "port": '5432',
           "database": 'decaf_storage',
           "user": 'pgdecaf',
           "password": 'pgdecafpw'
       })
       #db.drop_all()
       db.init_db()
       # Configure logging
       log_file = LOGFILE
       logger = logging.getLogger(__name__)
       logger.setLevel(logging.DEBUG)
       fh = logging.FileHandler(log_file)
       logger.addHandler(fh)

       self.storage = Storage(db, logger=logger)

   def test_scenario_insert(self):
       # create VNF
       code, vnf_id = self.storage.add(Vnf,{
           'name': 'name',
           'description': 'description',
           'path': 'path',
           'public': False
       })
       print('VNF: ', vnf_id)

       # create Image
       code, image_id = self.storage.add(Image,{
           'name': 'name',
           'description': 'description',
           'location': 'location'
       })
       print('Image: ', image_id)
       # create Flavor

       code, flavor_id = self.storage.add(Flavor,{
           'name': 'name',
           'description': 'description',
           'disk': 12,
           'ram': 8,
           'vcpus': 4
       })
       print('Flavor: ', flavor_id)

       # create VM
       code, vm_id = self.storage.add(Vm,{
           'name': 'name',
           'description': 'description',
           'vnf_id': vnf_id,
           'flavor_id': flavor_id,
           'image_id': image_id,
           'image_path': 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
       })
       print('VM: ', vm_id)

       # create Scenario
       code, sce_id = self.storage.add(Scenario, {
           'name': 'name',
           'description': 'description'
       })
       print('Scenario: ', sce_id)

       # add Vnf to Scenario
       code, scenario_vnf = self.storage.add(ScenarioVnf, {
           'name': 'name',
           'description': 'description',
           'scenario_id': sce_id,
           'vnf_id': vnf_id
       })
       print('Scenario VNF: ', scenario_vnf)

       code, vnfs = self.storage.get(Vnf,
                                     filters={'vnf.uuid': vnf_id},
                                     options=['vms', 'scenario_vnfs.scenario'])

       for vnf in vnfs:
           print(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
           vnf = json.loads(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
           print("VMS:\n", json.dumps(vnf['vms']))

if __name__ == '__main__':
   test=TestStorageAPI()
   test.test_scenario_insert()