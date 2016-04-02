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

import json
import traceback
from decaf_storage import Endpoint as Storage
from decaf_utils_components import BasePlugin, In
from decaf_utils_components.base_daemon import daemonize


class ExampleScaling(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(ExampleScaling, self).__init__(logger=logger, config=config)
        self.storage = None

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    def dispose(self):
        super(ExampleScaling, self).dispose()

    def _after_connect(self):
        """
        Is called after the daemon or plugin is started and fully registered against the RPC system.

        :return:
        """
        self.storage = Storage(self.rpc, self.logger)

    @In("scenario_instance_id", str)
    def setup_scale_up(self, scenario_instance_id=None):

        # Get the scenario_instance_id, if not given

        if scenario_instance_id is None:
            try:
                scenario_instance_id = self.get_scenario_instance_id()
            except BaseException as e:
                self.logger.error(str(e))
                return 500

        # find vms and subscribes to all vms
        vnf_instances = self.storage.get("vnf_instance",
                                         options=[
                                             "vm_instances"
                                         ],
                                         filters={
                                             "scenario_instance_id": scenario_instance_id,
                                             "name": "simplewebserver"
                                         })

        # subscribe to monitoring
        vm_instance_id = vnf_instances[0]["vm_instances"][0]['uuid']

        # greater than 50% cpu utilisation
        cpu_alarm_req = {
            "monitoring_alarm_request": {
                "type": "cpu_util",
                "vm_instance_id": vm_instance_id,
                "comparison_operator": "ge",
                "threshold": 50,
                "threshold_type": "relative",  # absolute
                "statistic": "max",  # min, avg
                "period": 60  # interval interleaving of monitoring sampling in seconds
            }
        }

        self.logger.debug("MONITORING: registering cpu alarm:")
        self.logger.debug(json.dumps(cpu_alarm_req))

        self.cpu_alarm_id = self.rpc.callSync(60, "decaf_masta.create_monitoring_alarm",
                                              cpu_alarm_req)

        self.rpc.subscribe(self.cpu_alarm_id, self.scale_up)

        return 200

    @In("monitoring_alarm_event", dict)
    def scale_up(self, monitoring_alarm_event):

        # check if there are too many vms deployed
        vms = self.storage.get('vm_instance', options=[], filters={})

        if len(vms) >= 6:
            self.logger.error("There are too many machines deployed. Does not scale up.")
            return 500

        self.logger.info("Scaling up...")

        monitoring_alarm_event = monitoring_alarm_event["monitoring_alarm_event"]

        self.rpc.unsubscribe(monitoring_alarm_event["subscription_name"])

        self.logger.debug("MONITORING ALARM received: %s" % json.dumps(monitoring_alarm_event))

        vm_instance_id = monitoring_alarm_event['monitoring_alarm_request']['vm_instance_id']

        vms = self.storage.get('vm_instance',
                               options=[
                                   'vm.vnf',
                                   'vnf_instance.scenario_instance',
                                   'vm.image'
                               ],
                               filters={
                                   'uuid': vm_instance_id
                               })

        vm = vms[0]['vm']
        vnf = vm['vnf']
        vnf_instance = vms[0]['vnf_instance']
        vnf_name = vnf['name']
        scenario_instance_id = vnf_instance["scenario_instance_id"]

        self.logger.debug("VM_INSTANCE_ID: " + vm_instance_id)
        self.logger.debug("VNF_NAME: " + vnf_name)
        self.logger.debug("EVENT: \n" + json.dumps(monitoring_alarm_event))

        # ------------------------
        # update storage component
        # ------------------------

        # add new vnf_instance
        new_vnf_instance = {
            'name': vnf['name'],
            'description': vnf['description'],
            'vnf_id': vnf['uuid'],
            'scenario_instance_id': vnf_instance['scenario_instance_id'],
            'datacenter_id': vnf_instance['datacenter_id']
        }
        try:
            new_vnf_instance_id = self.storage.add('vnf_instance', data=new_vnf_instance)
        except BaseException as e:
            self.logger.exception("Couldn't add vnf instance to storage.\n Exception was :\n {0}".format(e))
            return

        self.logger.debug("ADDED new vnf_instance: %s" % new_vnf_instance_id)

        # add new vm_instance
        new_vm_instance = {
            'name': vm['name'],
            'description': vm['description'],
            'vnf_instance_id': new_vnf_instance_id,
            'vm_id': vm['uuid']
        }

        try:
            new_vm_instance_id = self.storage.add('vm_instance', data=new_vm_instance)
        except BaseException as e:
            self.logger.exception("Couldn't add vm instance to storage.\n Exception was :\n {0}".format(e))
            return

        self.logger.debug("ADDED new vm_instance: %s" % new_vm_instance_id)

        # we know there is just a single vm inside the vnf -> no need to add other vms

        # find scenario_net between webserver and loadbalancer by vnf_instance
        try:
            vnf_instances = self.storage.get('vnf_instance',
                                             options=[
                                                 'scenario_interface_instances'
                                                 '.scenario_net_instance'
                                                 '.scenario_net'
                                                 '.scenario_interfaces'
                                                 '.scenario_vnf'
                                             ],
                                             filters={'uuid': vnf_instance['uuid']})
        except BaseException as e:
            self.logger.exception("Couldn't get vnf from storage.\n Exception was :\n {0}".format(e))
            return

        # there should be just a single vnf_instance
        vnf_instance = vnf_instances[0]

        # and a single scenario_interface_instances
        scenario_interface_instances = vnf_instance['scenario_interface_instances'][0]

        # and just a single scenario_net_instance
        scenario_net_instance = scenario_interface_instances['scenario_net_instance']
        scenario_net = scenario_net_instance['scenario_net']

        # add new scenario_net_instances
        new_scenario_net_instance = {
            'name': scenario_net['name'],
            'description': scenario_net['description'],
            'scenario_net_id': scenario_net['uuid'],
            'scenario_instance_id': scenario_instance_id,
            'type': scenario_net['type']
        }
        try:
            new_scenario_net_instance_id = self.storage.add('scenario_net_instance', data=new_scenario_net_instance)
        except BaseException as e:
            self.logger.exception(
                    """Couldn't add scenario net instance to storage.
                    Exception was :
                    {0}""".format(e))
            return

        self.logger.debug("ADDED new scenario_net_instance: %s" % new_scenario_net_instance_id)

        new_webserver_scenario_interface_instance_id = None
        new_loadbalancer_scenario_interface_instance_id = None
        loadbalancer_vnf_instance = None

        for scenario_interface in scenario_net['scenario_interfaces']:

            # check if this scenario_interface is for the webserver
            if scenario_interface['scenario_vnf']['vnf_id'] == vnf['uuid']:

                webserver_interface = self.storage.get('interface',
                                                                options=[],
                                                                filters={'uuid': scenario_interface['interface_id']})[0]
                new_webserver_interface_instance = {
                    'name': webserver_interface['name'],
                    'description': webserver_interface['description'],
                    'internal_name': webserver_interface['internal_name'],
                    'external_name': webserver_interface['external_name'],
                    'type': webserver_interface['type'],
                    'vpci': webserver_interface['vpci'],
                    'bw': webserver_interface['bw'],
                    'vm_instance_id': new_vm_instance_id,
                    #'net_instance_id': new_scenario_net_instance_id, #TODO make that correctly!
                    'interface_id': webserver_interface['uuid']
                }
                new_webserver_interface_instance_id = self.storage.add('interface_instance',
                                                                       data=new_webserver_interface_instance)

                # add scenario_interface_instances for the new webserver
                new_webserver_scenario_interface_instance = {
                    'name': scenario_interface['name'],
                    'description': scenario_interface['description'],
                    'vnf_instance_id': new_vnf_instance_id,
                    'scenario_net_instance_id': new_scenario_net_instance_id,
                    'interface_instance_id': new_webserver_interface_instance_id,
                    'scenario_interface_id': scenario_interface['uuid']
                }

                try:
                    new_webserver_scenario_interface_instance_id = \
                            self.storage.add('scenario_interface_instance',
                                             data=new_webserver_scenario_interface_instance)
                except BaseException as e:
                    self.logger.exception("""Couldn't add scenario_interface_instance to storage.
                    Exception was :
                    {0}""".format(e))
                    return

                self.logger.debug("ADDED new webserver_scenario_interface_instance: %s" %
                                  new_webserver_scenario_interface_instance_id)

            else:
                # this is scenario_interface is for the loadbalancer

                # get vnf_instance_id for the loadbalancer by scenario_net_instance

                try:
                    loadbalancer_vnf_instances = self.storage.get('vnf_instance',
                                                                  options=['vm_instances'],
                                                                  filters={'name': 'loadbalancer'})

                except BaseException as e:
                    self.logger.exception("""Couldn't get vnf instance from storage.
                    Exception was :
                    {0}""".format(e))
                    return

                loadbalancer_vnf_instance = loadbalancer_vnf_instances[0]

                loadbalancer_vm_instance_id = loadbalancer_vnf_instance['vm_instances'][0]['uuid']

                loadbalancer_interface = self.storage.get('interface',
                                                                    options=[],
                                                                    filters={'uuid': scenario_interface['interface_id']})[0]

                new_loadbalancer_interface_instance = {
                    'name': loadbalancer_interface['name'],
                    'description': loadbalancer_interface['description'],
                    'internal_name': loadbalancer_interface['internal_name'],
                    'external_name': loadbalancer_interface['external_name'],
                    'type': loadbalancer_interface['type'],
                    'vpci': loadbalancer_interface['vpci'],
                    'bw': loadbalancer_interface['bw'],
                    'vm_instance_id': loadbalancer_vm_instance_id,
                    #'net_instance_id': new_scenario_net_instance_id,
                    'interface_id': loadbalancer_interface['uuid']
                }

                new_loadbalancer_interface_instance_id = self.storage.add('interface_instance',
                                                                          data=new_loadbalancer_interface_instance)

                # add scenario_interface_instances for the new loadbalancer
                new_loadbalancer_scenario_interface_instance = {
                    'name': scenario_interface['name'],
                    'description': scenario_interface['description'],
                    'vnf_instance_id': loadbalancer_vnf_instance['uuid'],
                    'scenario_net_instance_id': new_scenario_net_instance_id,
                    'interface_instance_id': new_loadbalancer_interface_instance_id,
                    'scenario_interface_id': scenario_interface['uuid']
                }
                try:
                    new_loadbalancer_scenario_interface_instance_id = \
                        self.storage.add('scenario_interface_instance',
                                         data=new_loadbalancer_scenario_interface_instance)
                except BaseException as e:
                    self.logger.exception("""Couldn't add scenario interface to storage.
                    Exception was :
                    {0}""".format(e))
                    return
                self.logger.debug("ADDED new loadbalancer_scenario_interface_instance: %s" %
                                  new_loadbalancer_scenario_interface_instance_id)

        # send add_graph to masta

        try:
            datacenter = self.storage.get("datacenter", options=[], filters={"uuid": vnf_instance['datacenter_id']})[0]

        except BaseException as e:
            self.logger.error("Error fetching datacenter from Storage. Exception was :\n %s\n" % e)
            return

        graph_to_add = {
            "graph": {
                "scenario_instance_id": vnf_instance["scenario_instance_id"],

                "nodes": [
                    {
                        "vm_instance_id": new_vm_instance_id,
                        "name": "scaled-webserver",  # HEAVILY HARDCODED
                        "metadata": {
                            "datacenter": datacenter['datacenter_masta_id'],
                            "image": vm['image_id'],
                            "flavor": vm['flavor_id'],
                            "mgmt": "eth0",
                            # "mgmt_physical": "eth0",
                            # "mgmt_ip:" "192.170.0.1",
                            # "keypair": {
                            #    "keypair_id": 1,
                            #    "private_key": "blabla",
                            #    "public_key": "blabla",
                            #    "fingerprint": "blub"
                            # }
                        }
                    }
                ],
                "edges": [
                    {
                       "source": loadbalancer_vm_instance_id,
                       "type": "data",
                       "target": new_vm_instance_id,
                       "metadata": {
                            "source_internal": "int3",
                            "source_external": "data2",
                            "source_interface_instance_id": new_loadbalancer_interface_instance_id,
                            # "source_port_physical": "eth3",
                            # "source_port_ip": "10.0.2.10",
                            "target_internal": "xe0",
                            "target_external": "bla",
                            "target_interface_instance_id": new_webserver_interface_instance_id,
                            # "target_port_physical": "eth3",
                            # "target_port_ip": "10.0.2.11"
                       }
                    }
                ]
            }
        }

        self.logger.debug("DEPLOY new nodes with extend graph:")
        self.logger.debug(json.dumps(graph_to_add))

        self.extended_graph = self.rpc.callSync(60, "decaf_masta.extend_scenario",
                                                graph_to_add)

        # write graph data into DB

        # All nodes got annotated with the mgmt interface and the keypairs for SSH Access
        # -> Both need to be created in the database

        for node in self.extended_graph['graph']['nodes']:

            # -------- Create KEYPAIR Entry in database -------------
            try:

                self.logger.debug("ADDING Keypair for VM: {0}".format(node["vm_instance_id"]))

                node_keypair = node["metadata"]["keypair"]
                storage_keypair = {
                    "vm_instance_id":   node["vm_instance_id"],
                    "keypair_id":       node_keypair["keypair_id"],
                    "private_key":      node_keypair["private_key"],
                    "public_key":       node_keypair["public_key"],
                    "fingerprint":      node_keypair["fingerprint"],
                    "username":         vm['image']['username'],
                    "password":         vm['image']['password'],
                }
                self.storage.add('vm_instance_keypair', data=storage_keypair)

            except KeyError as k:
                self.logger.error("Keypair for VM {0} is missing or incomplete.\n Exception was:\n {1}"
                                  .format(node["vm_instance_id"], k))
                return
            except BaseException as e:
                self.logger.exception("Couldn't add keypair to storage.\n Exception was :\n {0}".format(e))
                return
            else:
                self.logger.debug("ADDED Keypair \n {0} \n for VM: {1}"
                                  .format(json.dumps(node_keypair, indent=4), node["vm_instance_id"]))

            # -------- Create Management Interface in database -------------

            try:

                self.logger.debug("ADDING Mgmt Interface for VM: {0}".format(node["vm_instance_id"]))

                # Get the Descriptor for the VM
                vm_id = self.storage.get('vm_instance',
                                         options=[],
                                         filters={'uuid': node['vm_instance_id']})[0]

                # Get the Descriptor for the MGMT Interface for that VM
                mgmt_interface = self.storage.get("interface",
                                                  options=[],
                                                  filters={
                                                      "vm_id": vm_id['vm_id'],
                                                      "type": "mgmt",
                                                  })[0]

                # Create the actual interface
                mgmt_interface_instance = {

                    "vm_instance_id":   node["vm_instance_id"],
                    "type":             "mgmt",
                    "interface_id":     mgmt_interface["uuid"],
                    "internal_name":    mgmt_interface["internal_name"],
                    "external_name":    mgmt_interface["external_name"],
                    "bw":               mgmt_interface["bw"],
                    "vpci":             mgmt_interface["vpci"],
                    "physical_name":    node["metadata"]["mgmt_physical"],
                    "ip_address":       node["metadata"]["mgmt_ip"],

                }

                # Add the interface to storage
                self.storage.add("interface_instance", data=mgmt_interface_instance)
            except KeyError as k:
                self.logger.error(k)
                return
            except BaseException as e:
                self.logger.exception(e)
                return
            else:
                self.logger.debug("ADDED Mgmt Interface for VM: {0}".format(node["vm_instance_id"]))

        # All edges got annotated with the physical port names and ip addresses

        edge = self.extended_graph['graph']['edges'][0] # there is only one edge

        try:
            self.logger.debug("EDGE : %s", json.dumps(edge, indent=4))

            # update loadbalancer
            self.storage.update('interface_instance',
                    uuid=edge['metadata']['source_interface_instance_id'],
                    data={
                        'physical_name': edge['metadata']['source_port_physical'],
                        'ip_address': edge['metadata']['source_port_ip']
                    })

            # update webserver
            self.storage.update('interface_instance',
                    uuid=edge['metadata']['target_interface_instance_id'],
                    data={
                        'physical_name': edge['metadata']['target_port_physical'],
                        'ip_address': edge['metadata']['target_port_ip']
                    })

        except BaseException as e:
            self.logger.error(e)

        # update VNF and VM Element managers

        self.rpc.callSync(900, 'decaf_vnf_manager_adapter.update')

        # add predecessor to loadbalancer

        self.rpc.callSync(300, str(loadbalancer_vm_instance_id) + ".create_interface",
                          iface_instance_id=edge['metadata']['source_interface_instance_id'])

        self.rpc.callSync(120, str(loadbalancer_vm_instance_id) + ".new_successor",
                          ip_address=edge['metadata']['target_port_ip'])

        self.logger.debug("FINISHED SCALING new graph is now:")
        self.logger.debug(json.dumps(self.extended_graph))

        return 200

    @In("scenario_instance_id", str)
    def setup_scale_down(self, scenario_instance_id=None):

        self.logger.info("Setup scale down...")

        # Get the scenario_instance_id, if not given

        if scenario_instance_id is None:
            try:
                scenario_instance_id = self.get_scenario_instance_id()
            except BaseException as e:
                self.logger.error(str(e))
                return 500

        # Get the webserver

        webserver_vnf_instances = self.storage.get("vnf_instance",
                               options=[
                                   "vm_instances"
                               ],
                               filters={
                                   "name": "simplewebserver",
                                   "scenario_instance_id": scenario_instance_id
                               })

        if len(webserver_vnf_instances) == 0:
            self.logger.error("There is no webserver VNF.")
            return 404

        webserver_index = 0 # take the old webserver
        webserver_vnf_instance = webserver_vnf_instances[webserver_index]
        webserver_vnf_instance_id = webserver_vnf_instance['uuid']

        if len(webserver_vnf_instance["vm_instances"]) == 0:
            self.logger.error("There are not VM instances of Webserver VNF " + str(webserver_vnf_instance_id) + ".")
            return 404

        webserver_vm_instance = webserver_vnf_instance["vm_instances"][0]
        webserver_vm_instance_id = webserver_vm_instance['uuid']

        # if in the last 30 seconds, the cpu utilization was max 10%
        cpu_alarm_request = {
            "monitoring_alarm_request": {
                "type": "cpu_util",
                "vm_instance_id": webserver_vm_instance_id,
                "comparison_operator": "le",
                "threshold": 10,
                "threshold_type": "relative",
                "statistic": "max",
                "period": 30
            }
        }

        self.logger.debug("Registering monitoring alarm...")

        self.logger.debug(json.dumps(cpu_alarm_request))

        self.cpu_alarm_id = self.rpc.callSync(60, "decaf_masta.create_monitoring_alarm",
                                              cpu_alarm_request)

        self.rpc.subscribe(self.cpu_alarm_id, self.scale_down)

        return 200

    @In("monitoring_alarm_event", dict)
    def scale_down(self, monitoring_alarm_event):

        self.logger.info("Scaling down...")

        monitoring_alarm_event = monitoring_alarm_event["monitoring_alarm_event"]

        self.rpc.unsubscribe(monitoring_alarm_event["subscription_name"])

        # Get the old webserver

        old_webserver_vm_instance_id = monitoring_alarm_event["monitoring_alarm_request"]["vm_instance_id"]

        old_webserver_vm_instances = self.storage.get("vm_instance", options=[],
                               filters={
                                   "uuid": old_webserver_vm_instance_id
                               })

        if len(old_webserver_vm_instances) == 0:
            self.logger.error("The Webserver VM instance with ID " + str(old_webserver_vm_instance_id) + " could not be found.")
            return 404

        old_webserver_vm_instance = old_webserver_vm_instances[0]

        old_webserver_vnf_instances = self.storage.get("vnf_instance", options=[],
                               filters={
                                   "uuid": old_webserver_vm_instance["vnf_instance_id"]
                               })

        old_webserver_vnf_instance = old_webserver_vnf_instances[0]

        scenario_instance_id = old_webserver_vnf_instance["scenario_instance_id"]

        # Get the new webserver

        webserver_vnf_instances = self.storage.get("vnf_instance", options=['vm_instances'],
                               filters={
                                   "scenario_instance_id": scenario_instance_id,
                                   "name": "simplewebserver"
                               })

        found = 0
        for vnf_instance in webserver_vnf_instances:
            if vnf_instance["vm_instances"][0]["uuid"] != old_webserver_vm_instance_id:
                webserver_vnf_instance = vnf_instance
                webserver_vnf_instance_id = webserver_vnf_instance["uuid"]
                webserver_vm_instance = vnf_instance["vm_instances"][0]
                webserver_vm_instance_id = webserver_vm_instance["uuid"]
                found += 1

        if found == 0:
            self.logger.error("There is no scaled webserver in the database.")
            return 404

        if found > 1:
            self.logger.warning("There is more than one scaled webserver. One arbitrary will be deleted.")

        # Get the loadbalancer

        loadbalancer_vnf_instances = self.storage.get("vnf_instance",
                               options=[
                                   "vm_instances"
                               ],
                               filters={
                                   "name": "loadbalancer",
                                   "scenario_instance_id": scenario_instance_id
                               })

        if len(loadbalancer_vnf_instances) == 0:
            self.logger.error("There is no loadbalancer VNF.")
            return 404

        loadbalancer_vnf_instance = loadbalancer_vnf_instances[0]
        loadbalancer_vnf_instance_id = loadbalancer_vnf_instance['uuid']

        if len(loadbalancer_vnf_instance["vm_instances"]) == 0:
            self.logger.error("There are no VM instances of Loadbalancer VNF " + str(loadbalancer_vnf_instance_id) + ".")
            return 404

        loadbalancer_vm_instance = loadbalancer_vnf_instance["vm_instances"][0]
        loadbalancer_vm_instance_id = loadbalancer_vm_instance["uuid"]


        # Create the instance graph and send to masta

        instance_graph = {
            "graph": {
                "scenario_instance_id": str(scenario_instance_id),
                "nodes": [
                    {
                        "vm_instance_id": str(webserver_vm_instance_id)
                    }
                ]
            }
        }

        self.extended_graph = self.rpc.callSync(60, "decaf_masta.shrink_scenario",
                                                    instance_graph)


        # Get scenario interface instance of the webserver

        webserver_scenario_interface_instances = self.storage.get("scenario_interface_instance",
                                                options=[],
                                                filters={
                                                    "vnf_instance_id": webserver_vnf_instance_id
                                                })

        if len(webserver_scenario_interface_instances) == 0:
            self.logger.error("There is no scenario interface instance for Webserver VNF " + str(webserver_vnf_instance_id) + ".")
            return 404
        elif len(webserver_scenario_interface_instances) > 1:
            self.logger.error("There is more than one scenario interface instance for Webserver VNF " + str(webserver_vnf_instance_id) + ".")#
            return 500

        webserver_scenario_interface_instance = webserver_scenario_interface_instances[0]
        scenario_net_instance_id = webserver_scenario_interface_instance["scenario_net_instance_id"]

        # Find webserver interface instances, get IP Address

        webserver_interface_instances = self.storage.get("interface_instance", options=[],
                               filters={
                                   "vm_instance_id": webserver_vm_instance_id
                               })

        webserver_ip_address = None

        for webserver_interface_instance in webserver_interface_instances:
            if webserver_interface_instance["uuid"] == webserver_scenario_interface_instance["interface_instance_id"]:
                webserver_ip_address = webserver_interface_instance["ip_address"]

        if webserver_ip_address is None:
            self.logger.error("The IP address of the webserver with VM instance ID " + str(webserver_vm_instance_id) + " could not be resolved.")
            return 404

        # Delete successor from loadbalancer

        try:
            self.rpc.callSync(120, str(loadbalancer_vm_instance_id) + ".delete_successor",
                                ip_address=webserver_ip_address)
        except BaseException as e:
            self.logger.error("There was an error while removing the webserver IP from the loadbalancer.")

        # Delete webserver interface instances

        for webserver_interface_instance in webserver_interface_instances:
            self.storage.delete('interface_instance',
                            uuid=webserver_interface_instance["uuid"])

        # Delete webserver scenario interface instance

        self.storage.delete('scenario_interface_instance',
                            uuid=webserver_scenario_interface_instance["uuid"])



        # Get the scenario interface instance of the loadbalancer

        loadbalancer_scenario_interface_instances = self.storage.get("scenario_interface_instance",
                                                options=[],
                                                filters={
                                                    "scenario_net_instance_id": scenario_net_instance_id,
                                                    "vnf_instance_id": loadbalancer_vnf_instance_id
                                                })

        if len(loadbalancer_scenario_interface_instances) == 0:
            self.logger.error("There is no scenario interface instance for Loadbalancer VNF " + str(loadbalancer_vnf_instance_id) + ".")
            return 404
        elif len(loadbalancer_scenario_interface_instances) > 1:
            self.logger.error("There is more than one scenario interface instance for Loadbalancer VNF " + str(loadbalancer_vnf_instance_id) + ".")#
            return 500

        loadbalancer_scenario_interface_instance = loadbalancer_scenario_interface_instances[0]
        loadbalancer_scenario_interface_instance_id = loadbalancer_scenario_interface_instance["uuid"]

        # Find loadbalancer interface instances

        loadbalancer_interface_instances = self.storage.get("interface_instance", options=[],
                               filters={
                                   "uuid": loadbalancer_scenario_interface_instance["interface_instance_id"]
                               })

        if len(loadbalancer_interface_instances) == 0:
            self.logger.error("There is no interface instance for Loadbalancer VM " + str(loadbalancer_vm_instance_id) + ".")
            return 404

        loadbalancer_interface_instance = loadbalancer_interface_instances[0]
        loadbalancer_interface_instance_id = loadbalancer_interface_instance["uuid"]

        # Delete loadbalancer interface instance from VM

        try:
            self.rpc.callSync(300, str(loadbalancer_vm_instance_id) + ".delete_interface",
                                iface_instance_id=loadbalancer_interface_instance_id)
        except BaseException as e:
            self.logger.error("There was an error while deleting the interface of the loadbalancer.")

        # Delete loadbalancer interface instance

        self.storage.delete('interface_instance',
                            uuid=loadbalancer_interface_instance_id)

        # Delete loadbalancer scenario interface instance

        self.storage.delete('scenario_interface_instance',
                            uuid=loadbalancer_scenario_interface_instance_id)


        # Delete scenario net instance

        self.storage.delete('scenario_net_instance',
                            uuid=scenario_net_instance_id)


        # Delete VM instance keypair

        vm_instance_keypairs = self.storage.get("vm_instance_keypair", options=[],
                               filters={
                                   "vm_instance_id": webserver_vm_instance_id
                               })

        if len(vm_instance_keypairs) == 0:
            self.logger.error("There is VM instance keypair for webserver with id " + str(webserver_vm_instance_id) + ".")
            return 404
        elif len(vm_instance_keypairs) > 1:
            self.logger.error("There is more than one VM instance keypair for webserver with id " + str(webserver_vm_instance_id) + ".")
            return 500

        vm_instance_keypair = vm_instance_keypairs[0]

        self.storage.delete('vm_instance_keypair',
                            uuid=vm_instance_keypair["uuid"])


        # Delete VNF instance and VM instance

        self.storage.delete('vm_instance',
                        uuid=webserver_vm_instance_id)

        self.storage.delete('vnf_instance',
                        uuid=webserver_vnf_instance_id)


        # Update VNF Manager Adapter

        self.rpc.callSync(60, 'decaf_vnf_manager_adapter.update')

        return 200

    def get_scenario_instance_id(self):

        scenario_instances = self.storage.get("scenario_instance", options=[], filters={})

        if len(scenario_instances) == 0:
            raise BaseException("There is no scenario instance in the database.")

        if len(scenario_instances) > 1:
            raise BaseException("There is more than one scenario instance in the database.")

        return scenario_instances[0]["uuid"]

def daemon():
    daemonize(ExampleScaling)

if __name__ == '__main__':
    daemon()
