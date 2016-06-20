__author__ = 'Kristian Hinnenthal'

import json
import time
import tests.example_datatypes as ex
import twisted.internet.defer as defer
import unittest
from decaf_utils_protocol_stack import RpcLayer
import sys
import copy

def printer( *args, **kwargs):
    print args

class RPCTester(object):

    def __init__(self):
        self.rpc = RpcLayer(u'amqp://fg-cn-sandman1.cs.upb.de:5672', logger=None)

    def test_deploy(self, deploy_graph):
        result = self.rpc.callSync(60, "decaf_masta.deploy_scenario", deploy_graph)
        print(result)
        print(result["graph"]["nodes"][0]["metadata"]["keypair"]["private_key"].replace('\\n', '\n'))

    def test_extend(self, add_graph):
        result = self.rpc.callSync(60, "decaf_masta.extend_scenario", add_graph)
        print(result)

    def test_shrink(self, shrink_graph):
        result = self.rpc.callSync(60, "decaf_masta.shrink_scenario", shrink_graph)
        print(result)

    def test_destroy(self, scenario_instance_id):
        result = self.rpc.callSync(60, "decaf_masta.destroy_scenario", scenario_instance_id)
        print(result)

    def destroy_all_scenarios(self):
        result = self.rpc.callSync(60, "decaf_masta.destroy_all_scenarios")
        print(result)

    def delete_all_monitoring_alarms(self):
        result = self.rpc.callSync(60, "decaf_masta.delete_all_monitoring_alarms")
        print(result)

    def get_datacenter_ip_namespace(self, datacenter_id):
        result = self.rpc.callSync(60, "decaf_masta.get_datacenter_ip_namespace", datacenter_id)
        print(result)

    def create_flavor(self, flavor_data):
        result = self.rpc.callSync(60, "decaf_masta.create_flavor", flavor_data)
        print(result)

    def delete_flavor(self, flavor_id):
        result = self.rpc.callSync(60, "decaf_masta.delete_flavor", flavor_id)
        print(result)

    def create_image(self, image_data):
        result = self.rpc.callSync(60, "decaf_masta.create_image", image_data)
        print(result)

    def delete_image(self, image_id):
        result = self.rpc.callSync(60, "decaf_masta.delete_image", image_id)
        print(result)

    def create_keystone_credentials(self, credentials):
        result = self.rpc.callSync(60, "decaf_masta.create_keystone_credentials", credentials)
        print(result)

    def initialize_datacenter(self, datacenter_config):
        result = self.rpc.callSync(60, "decaf_masta.initialize_datacenter", datacenter_config)
        print(result)

    def action_vm_instance(self, vm_action):
        result = self.rpc.callSync(60, "decaf_masta.action_vm_instance", vm_action)
        print(result)

    def get_monitoring_data(self, monitoring_data):
        result = self.rpc.callSync(60, "decaf_masta.get_monitoring_data", monitoring_data)
        print(result)

    def create_monitoring_alarm(self, monitoring_alarm_request):
        result = self.rpc.callSync(60, "decaf_masta.create_monitoring_alarm", monitoring_alarm_request)
        return(result)

    def delete_monitoring_alarm(self, monitoring_alarm_id):
        result = self.rpc.callSync(60, "decaf_masta.delete_monitoring_alarm", monitoring_alarm_id)
        print(result)

    def vnf_manager_create_interface(self, interface_instance_id):
        result = self.rpc.callSync(60, "6c7aac08-4cb2-4655-9634-e87010e49a20.create_interface", iface_instance_id=interface_instance_id)
        print(result)

    def vnf_manager_delete_interface(self, interface_instance_id):
        result = self.rpc.callSync(60, "6c7aac08-4cb2-4655-9634-e87010e49a20.delete_interface", iface_instance_id=interface_instance_id)
        print(result)

    def new_successor(self, ip_address):
        result = self.rpc.callSync(60, "6c7aac08-4cb2-4655-9634-e87010e49a20.new_successor", ip_address=ip_address)
        print(result)

    def delete_successor(self, ip_address):
        result = self.rpc.callSync(60, "6c7aac08-4cb2-4655-9634-e87010e49a20.delete_successor", ip_address=ip_address)
        print(result)

    def scale_up(self, monitoring_alarm_event):
        result = self.rpc.callSync(60, "decaf_example_scaling.scale_up", monitoring_alarm_event=monitoring_alarm_event)
        print(result)

    def scale_down(self, monitoring_alarm_event):
        result = self.rpc.callSync(60, "decaf_example_scaling.scale_down", monitoring_alarm_event=monitoring_alarm_event)
        print(result)

    def end(self):
        self.rpc.dispose()

if __name__ == '__main__':

    tester = RPCTester()

    if sys.argv[1] == "scale_up":
        monitoring_alarm_event = {
            "monitoring_alarm_event": {
                "subscription_name": "nonsense",
                "value": 100,
                "monitoring_alarm_request": {
                    "vm_instance_id": sys.argv[2],
                }
            }
        }
        tester.scale_up(monitoring_alarm_event)
        tester.end()

    if sys.argv[1] == "scale_down":
        monitoring_alarm_event = {
            "monitoring_alarm_event": {
                "subscription_name": "nonsense",
                "value": 10,
                "monitoring_alarm_request": {
                    "vm_instance_id": sys.argv[2],
                }
            }
        }
        tester.scale_down(monitoring_alarm_event)
        tester.end()

    if sys.argv[1] == "create_interface":
        tester.vnf_manager_create_interface(sys.argv[2])
        tester.end()

    if sys.argv[1] == "delete_interface":
        tester.vnf_manager_delete_interface(sys.argv[2])
        tester.end()

    if sys.argv[1] == "new_successor":
        tester.new_successor(sys.argv[2])
        tester.end()

    if sys.argv[1] == "delete_successor":
        tester.delete_successor(sys.argv[2])
        tester.end()

    if sys.argv[1] == "deploy":
        tester.test_deploy(ex.bigger_deploy_graph)
        tester.end()

    if sys.argv[1] == "extend":
        tester.test_extend(ex.small_add_graph)
        tester.end()

    if sys.argv[1] == "shrink":
        tester.test_shrink(ex.shrink_graph)
        tester.end()

    if sys.argv[1] == "destroy":
        tester.test_destroy(sys.argv[2])
        tester.end()

    if sys.argv[1] == "destroy_all_scenarios":
        tester.destroy_all_scenarios()
        tester.end()

    if sys.argv[1] == "create_image":
        tester.create_image(ex.image_webserver_test)
        tester.end()

    if sys.argv[1] == "delete_image":
        tester.delete_image(sys.argv[2])
        tester.end()

    if sys.argv[1] == "action_vm_instance":
        vm_action = {
            "vm_action": {
                "vm_instance_id": "webserver-2-id",
                "action": sys.argv[2]
            }
        }
        tester.action_vm_instance(vm_action)
        tester.end()

    if sys.argv[1] == "get_monitoring_data":
        tester.get_monitoring_data(ex.monitoring_data)
        tester.end()

    if sys.argv[1] == "create_monitoring_alarm":
        subscription_name = tester.create_monitoring_alarm(ex.monitoring_alarm_request)
        tester.rpc.subscribe(subscription_name, printer)

    if sys.argv[1] == "delete_monitoring_alarm":
        tester.delete_monitoring_alarm(sys.argv[2])
        tester.end()

    #tester.get_datacenter_ip_namespace(1)
    #tester.delete_image("webserver-test-image-id")
    #tester.destroy_all_scenarios()
    #tester.delete_all_monitoring_alarms()
    #tester.create_keystone_credentials(ex.keystone_creds)
    #tester.initialize_datacenter(ex.datacenter_config)
    #tester.create_flavor(ex.flavor_data_test)
    #tester.delete_flavor("test-flavor-id-2")
    #tester.create_image(ex.image_data)

    #tester.end()


def doWork():
    pass
    #result = (yield r.call("decaf-masta.new_flavor",json.dumps(ex.flavor_data)))
    #print(result)
    #result = (yield r.call("decaf-masta.new_image",json.dumps(ex.image_data)))
    #print(result)
    #result = (yield r.call("decaf-masta.delete_flavor","7defe24d5b9a488fbd7718228375af3a"))
    #print(result)
    #result = (yield  r.call("decaf-masta.delete_image","94ef3cc424f943e68b06fdb52d9eead4"))
    #print(result)

    #time.sleep(8)

    #result = (yield r.call("decaf_masta.deploy_scenario",ex.small_deploy_graph))
    #print(result)
    #result = (yield r.call("decaf_masta.destroy_scenario","103b704af8bb4a24b0afebc8108f327c"))
    #print(result)

    #result = (yield  r.call("decaf-masta.delete_flavor","bla"))
    #d = r.call("decaf-masta.delete_image","695549fcc24146b1ba1fb7125f227a5f")
    #d = r.call("decaf-masta.get_datacenters")
    #d = r.call("decaf-masta.functions")

    #alarm_id = (yield r.call("decaf_masta.create_monitoring_alarm", ex.monitoring_alarm_request))
    #print alarm_id
    #r.subscribe(alarm_id, printer)
    #print "Subscribe OK"

    #d = r.call("decaf-masta.delete_monitoring_alarm","masta.alarm.9")

    #d = r.call("decaf-masta.get_monitoring_data",json.dumps(ex.monitoring_data_2))

    #print(result)

    #r.dispose()