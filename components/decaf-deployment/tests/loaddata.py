#!/usr/bin/env python
__author__ = 'tarun'

import json
import logging
from decaf_storage.json_base import StorageJSONEncoder
from decaf_storage.database import Database
from decaf_storage.model.scenario import Scenario
from decaf_storage.storage import Storage
from decaf_storage.model.flavor import Flavor
from decaf_storage.model.image import Image
from decaf_storage.model.scenario import Scenario
from decaf_storage.model.scenario_vnf import ScenarioVnf
from decaf_storage.model.vm import Vm
from decaf_storage.model.vnf import Vnf
from decaf_storage.model.interface import Interface
from decaf_storage.model.net import Net
from decaf_storage.model.scenario_net import ScenarioNet
from decaf_storage.model.scenario_interface import ScenarioInterface



LOGFILE = '/var/log/decaf/loaddata.log'

#class TestStorageAPI(unittest.TestCase):
class TestStorageAPI():

    def __init__(self):
        db = Database({
            "type": 'postgresql',
            #"host": 'fg-cn-decaf-head1.cs.upb.de',
            "host": '127.0.0.1',
            "port": '5432',
            "database": 'decaf_storage',
            "user": 'pgdecaf',
            "password": 'pgdecafpw'
        })
        #db.drop_all()
        #db.init_db()
        # Configure logging
        log_file = LOGFILE
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_file)
        logger.addHandler(fh)

        self.storage = Storage(db, logger=logger)

    def test_scenario_insert(self):
        # create VNF
        code, vnf_id1 = self.storage.add(Vnf,{
            'name': 'firewall',
            'description': 'firewall description',
            'path': 'path',
            'public': False
        })
        print('VNF: ', vnf_id1)

        code, vnf_id2 = self.storage.add(Vnf,{
            'name': 'loadbalancer',
            'description': 'loadbalancer description',
            'path': 'path',
            'public': False
        })
        print('VNF: ', vnf_id2)

        code, vnf_id3 = self.storage.add(Vnf,{
            'name': 'webserver',
            'description': 'webserver description',
            'path': 'path',
            'public': False
        })
        print('VNF: ', vnf_id3)

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
            'ram': 512,
            'vcpus': 4
        })
        print('Flavor: ', flavor_id)

        # create VM
        code, vm_id1 = self.storage.add(Vm,{
            'name': 'firewall',
            'description': 'firewall description',
            'vnf_id': vnf_id1,
            'flavor_id': flavor_id,
            'image_id': image_id,
            'image_path': 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
        })
        print('VM: ', vm_id1)

        # create VM
        code, vm_id2 = self.storage.add(Vm,{
            'name': 'loadbanalcer',
            'description': 'loadbanalcer description',
            'vnf_id': vnf_id2,
            'flavor_id': flavor_id,
            'image_id': image_id,
            'image_path': 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
        })
        print('VM: ', vm_id2)

        # create VM
        code, vm_id3 = self.storage.add(Vm,{
            'name': 'webserver',
            'description': 'webserver description',
            'vnf_id': vnf_id3,
            'flavor_id': flavor_id,
            'image_id': image_id,
            'image_path': 'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img'
        })
        print('VM: ', vm_id3)

        # create Scenario
        code, sce_id = self.storage.add(Scenario, {
            'name': 'testscenario',
            'description': 'testscenario description'
        })
        print('Scenario: ', sce_id)

        # add Vnf to Scenario
        code, scenario_vnf1 = self.storage.add(ScenarioVnf, {
            'name': 'name',
            'description': 'description',
            'scenario_id': sce_id,
            'vnf_id': vnf_id1
        })
        print('Scenario VNF: ', scenario_vnf1)

        # add Vnf to Scenario
        code, scenario_vnf2 = self.storage.add(ScenarioVnf, {
            'name': 'name',
            'description': 'description',
            'scenario_id': sce_id,
            'vnf_id': vnf_id2
        })
        print('Scenario VNF: ', scenario_vnf2)

        # add Vnf to Scenario
        code, scenario_vnf3 = self.storage.add(ScenarioVnf, {
            'name': 'name',
            'description': 'description',
            'scenario_id': sce_id,
            'vnf_id': vnf_id3
        })
        print('Scenario VNF: ', scenario_vnf3)

        # code, vnfs = self.storage.get(Vnf,
        #                               filters={'vnf.uuid': vnf_id},
        #                               options=['vms', 'scenario_vnfs.scenario'])
        #
        # for vnf in vnfs:
        #     print(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
        #     vnf = json.loads(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))
        #     print("VMS:\n", json.dumps(vnf['vms']))

        # add Net to VNF
        #code, net_id = self.storage.add(Net, {
        #    'name': 'name',
        #    'description': 'description',
        #    'type': 'data',
        #    'vnf_id': vnf_id
        #})
        #print('NET: ', net_id)

        # add Interface
        code, interface_id11 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'mgmt',
            'internal_name': 'mgmt0',
            'external_name': 'mgmt0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id1
        })
        print('INTERFACE: ', interface_id11)

        # add Interface
        code, interface_id12 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth0',
            'external_name': 'data0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id1
        })
        print('INTERFACE: ', interface_id12)

        # add Interface
        code, interface_id13 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth1',
            'external_name': 'data1',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id1
        })
        print('INTERFACE: ', interface_id13)

        # add Interface
        code, interface_id21 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'mgmt',
            'internal_name': 'mgmt0',
            'external_name': 'mgmt0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id2
        })
        print('INTERFACE: ', interface_id21)

        # add Interface
        code, interface_id22 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth0',
            'external_name': 'data0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id2
        })
        print('INTERFACE: ', interface_id22)

        # add Interface
        code, interface_id23 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth1',
            'external_name': 'data1',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id2
        })
        print('INTERFACE: ', interface_id23)

        # add Interface
        code, interface_id31 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'mgmt',
            'internal_name': 'mgmt0',
            'external_name': 'mgmt0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id3
        })
        print('INTERFACE: ', interface_id31)

        # add Interface
        code, interface_id32 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth0',
            'external_name': 'data0',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id3
        })
        print('INTERFACE: ', interface_id32)

        # add Interface
        code, interface_id33 = self.storage.add(Interface, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'internal_name': 'eth1',
            'external_name': 'data1',
            'vpci': '0000:00:11.0',
            'bw': 100,
            'vm_id': vm_id3
        })
        print('INTERFACE: ', interface_id33)

        # add Net to Scenario
        code, scenario_net_id01 = self.storage.add(ScenarioNet, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'scenario_id': sce_id
        })
        print('SCENARIO NET: ', scenario_net_id01)

        # add Net to Scenario
        code, scenario_net_id12 = self.storage.add(ScenarioNet, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'scenario_id': sce_id
        })
        print('SCENARIO NET: ', scenario_net_id12)

        # add Net to Scenario
        code, scenario_net_id23 = self.storage.add(ScenarioNet, {
            'name': 'name',
            'description': 'description',
            'type': 'data',
            'scenario_id': sce_id
        })
        print('SCENARIO NET: ', scenario_net_id23)

        # add Interface to Scenario
        code, scenario_int_id12 = self.storage.add(ScenarioInterface, {
            'name': 'name',
            'description': 'description',
            'scenario_vnf_id': scenario_vnf1,
            'scenario_net_id': scenario_net_id12,
            'interface_id': interface_id13,
            'public': False
        })
        print('SCENARIO INTERFACE: ', scenario_int_id12)

        # add Interface to Scenario
        code, scenario_int_id21 = self.storage.add(ScenarioInterface, {
            'name': 'name',
            'description': 'description',
            'scenario_vnf_id': scenario_vnf2,
            'scenario_net_id': scenario_net_id12,
            'interface_id': interface_id22,
            'public': False
        })
        print('SCENARIO INTERFACE: ', scenario_int_id21)

        # add Interface to Scenario
        code, scenario_int_id22 = self.storage.add(ScenarioInterface, {
            'name': 'name',
            'description': 'description',
            'scenario_vnf_id': scenario_vnf2,
            'scenario_net_id': scenario_net_id23,
            'interface_id': interface_id23,
            'public': False
        })
        print('SCENARIO INTERFACE: ', scenario_int_id22)

        # add Interface to Scenario
        code, scenario_int_id31 = self.storage.add(ScenarioInterface, {
            'name': 'name',
            'description': 'description',
            'scenario_vnf_id': scenario_vnf3,
            'scenario_net_id': scenario_net_id23,
            'interface_id': interface_id32,
            'public': False
        })
        print('SCENARIO INTERFACE: ', scenario_int_id31)

        # add Interface to Scenario
        code, scenario_int_id01 = self.storage.add(ScenarioInterface, {
            'name': 'name',
            'description': 'description',
            'scenario_vnf_id': scenario_vnf1,
            'scenario_net_id': scenario_net_id01,
            'interface_id': interface_id12,
            'public': True
        })
        print('SCENARIO INTERFACE: ', scenario_int_id01)

if __name__ == '__main__':
    test=TestStorageAPI()
    test.test_scenario_insert()
