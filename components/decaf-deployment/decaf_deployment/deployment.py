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

import decaf_storage
from decaf_utils_components.base_daemon import daemonize

from decaf_utils_components import BasePlugin, In, Out


class Deployment(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(Deployment, self).__init__(logger=logger, config=config)
        # List to keep all the vm instances created as part of current deployment
        self.vm_instance_list = []
        # List to keep all the vnf instances created as part of current deployment
        self.vnf_instance_list = []
        # To hold current scenario instance
        self.current_scenario_instance = None
        # To contain the graph prepared for deplyoment
        self.deploy_graph = {}
        # To contain the graph returned from MaSta
        self.instance_graph = {}

    def _after_connect(self):
        self.s = decaf_storage.Endpoint(self.rpc, self.logger)

    @In("scenario_id", str)
    @In("scenario_instance_name", str)
    @In("scenario_instance_description", str)
    @Out("scenario_instance_id", str)
    def deploy_scenario(self, scenario_id, scenario_instance_name, scenario_instance_description):
        """
        This function retrieve all the VNF, VM, interfaces from Storage associated to the specific scenario
        and also get the placement graph from Placement component and prepare a deployment graph dictionary.
        After that request MaSta to deploy the scenario, which interns deploy all the VM and start them.
        MaSta return a instance graph (dictionary) with some additional information in the deploy graph
        for example IPs of the interfaces and key pair of the VMs. These information are stored in
        the Storage for further reference. This function also call VNFM adapter to start VNF Manager
        and Element Manager.

        :param scenario_id: String contains the UUID of the Scenario to be deployed.
        :param scenario_instance_name: String contains the expected name of the Scenario Instance.
        :param scenario_instance_description: String contains the expected description of the
         Scenario Instance.
        :return: A string scenario_instance_id (UUID) of the created Scenario Instance.
         In case of error return the error code as string.
        """
        result = 200
        self.current_scenario_instance = None
        try:
            self.logger.debug("Checking that the scenario_id exists and getting the scenario dictionary")
            scenarios = self.s.get('scenario', options=[], filters={'uuid': scenario_id})
            if len(scenarios) == 0:
                self.logger.warn("deploy_scenario: There is no scenario exist with scenario id %s", scenario_id)
                return 404

            # self.logger.debug("Create scenario instance to deploy")
            scenario_instance = {
                'name': scenario_instance_name,
                'description': scenario_instance_description,
                'scenario_id': scenario_id
            }
            scenario_instance_id = self.s.add('scenario_instance', data=scenario_instance)
            self.current_scenario_instance = scenario_instance_id
            scenario_instances = self.s.get('scenario_instance', options=[],
                                            filters={'uuid': scenario_instance_id})
            scenario_instance = scenario_instances[0]

            # Initialize these variable
            self.vm_instance_list = []
            self.vnf_instance_list = []
            self.deploy_graph = {
                'graph': {
                    'scenario_instance_id': scenario_instance_id,
                    'nodes': [],
                    'edges': [],
                    'public_ports': []
                }
            }
            self.instance_graph = {}

            # Prepare the nodes dta in the graph
            result = self.__populate_nodes__(scenario_instance)
            if result != 200:
                self.logger.error("deploy_scenario: Node population in the graph failed.")
                return result
            # Prepare the edges in the graph
            self.__populate_edges__(scenario_instance)

            self.logger.debug("DEPLOYMENT GRAPH: %s", json.dumps(self.deploy_graph, indent=4))
            # MaSta return a modified instance graph if the scenario deployed successfully otherwise 500 as error code.
            result = self.rpc.callSync(600, 'decaf_masta.deploy_scenario', instance_graph=self.deploy_graph)

            if result == 500:  # Error code from MaSta
                self.logger.error("scenario_start: deploy scenario failed at decaf_masta")
                self.destroy_scenario_instance(self.current_scenario_instance)
                return result
            else:  # MaSta return the deployed instance graph (dictionary) for successful deployment of scenario
                self.instance_graph = result
                # self.instance_graph = self.deploy_graph  # testing

                self.logger.debug("INSTANCE GRAPH received from MaSta: %s", json.dumps(self.instance_graph, indent=4))

                self.__update_node_info__(self.instance_graph['graph']['nodes'])
                self.__update_edge_info__(self.instance_graph['graph']['edges'])
                self.__update_public_port_info__(self.instance_graph['graph']['public_ports'])

                # self.logger.debug("==================Deployment done==========")

        except BaseException, e:
            self.logger.error(e)
            self.destroy_scenario_instance(self.current_scenario_instance)
            raise e
        else:
            # We put the VNF out of the rollback stuff, because its still in debug phase

            self.rpc.callSync(900, 'decaf_vnf_manager_adapter.update')

            # For every edge, inform source and target
            for edge in self.instance_graph['graph']['edges']:

                source_rpc_address = edge['source']  # This is a VM instance id
                target_ip_address = edge['metadata']['target_port_ip']

                self.rpc.callSync(180, source_rpc_address + ".new_successor",
                                  ip_address=target_ip_address)

            return self.current_scenario_instance

    @In("scenario_id", str)
    @Out("all_scenario_graph", str)
    def view_all_scenario_instances(self, scenario_id=None):
        """
        This function check if there is any scenario instance available for the specified scenario id
        then it return a dictionary with all scenario instances and its associated VNF instances,
        VM instances, and its key pairs/credentials to access the VM. If no scenario_id specified,
        it list out all instances of all scenario in Storage.

        :param scenario_id: String contains the UUID of the Scenario to be displayed.
        :return: A python dictionary as string, contains the instances of the specified Scenario
         or of all Scenario. In case of error return the error code as string.
        """
        try:
            all_scenario_graph = []
            if scenario_id is None:
                scenarios = self.s.get('scenario', options=[], filters={})
                if len(scenarios) == 0:
                    self.logger.warn("view_all_scenario_instances error. Scenario not found")
                    return 404
                for scenario in scenarios:
                    scenario_graph = self.__view_scenario_instance__(scenario)
                    all_scenario_graph.append(scenario_graph)
            else:
                scenarios = self.s.get('scenario', options=[], filters={'uuid': scenario_id})
                if len(scenarios) == 0:
                    self.logger.warn("view_all_scenario_instances error. Scenario not found")
                    return 404
                scenario_graph = self.__view_scenario_instance__(scenarios[0])
                all_scenario_graph.append(scenario_graph)

            return all_scenario_graph
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __view_scenario_instance__(self, scenario):
        """
        This function check if there is any scenario instance available for the scenario
        then it return a dictionary with  all scenario instances and its associated VNF instances,
        VM instances, and its keypairs/credentials to access the VM.

        :param scenario:
        :return scenario_graph:
        """
        try:

            scenario_graph = {
                'scenario_uuid': scenario['uuid'],
                'scenario_name': scenario['name'],
                'scenario_description': scenario['description'],
                'scenario_instances': []
            }

            scenario_instances = self.s.get('scenario_instance',
                                            options=[],
                                            filters={'scenario_id': scenario['uuid']})
            if len(scenario_instances) == 0:
                self.logger.info("view_all_scenario_instances info, There is no scenario instance exist for the scenario %s",
                                 scenario['uuid'])
                scenario_graph['scenario_instances'].append("There is no scenario instance.")
            else:
                for scenario_instance in scenario_instances:
                    scenario_instance_graph = {
                        'scenario_instance_uuid': scenario_instance['uuid'],
                        'scenario_instance_name': scenario_instance['name'],
                        'scenario_instance_description': scenario_instance['description'],
                        'vnf_instances': []
                    }
                    vnf_instances = self.s.get('vnf_instance',
                                               options=[],
                                               filters={'scenario_instance_id': scenario_instance['uuid']})
                    for vnf_instance in vnf_instances:
                        vnf_instance_graph = {
                            'vnf_instance_uuid': vnf_instance['uuid'],
                            'vnf_instance_name': vnf_instance['name'],
                            'vnf_instance_description': vnf_instance['description'],
                            'vm_instances': []
                        }
                        vm_instances = self.s.get('vm_instance',
                                                  options=[],
                                                  filters={'vnf_instance_id': vnf_instance['uuid']})
                        for vm_instance in vm_instances:
                            interface_instances = self.s.get('interface_instance', options=[],
                                                             filters={'vm_instance_id': vm_instance['uuid'],
                                                                      'type': 'mgmt'})
                            vm_instance_keypairs = self.s.get('vm_instance_keypair',
                                                              options=[],
                                                              filters={'vm_instance_id': vm_instance['uuid']})
                            vm_instance_graph = {
                                'vm_instance_uuid': vnf_instance['uuid'],
                                'vm_instance_name': vnf_instance['name'],
                                'vm_instance_description': vnf_instance['description'],
                                'vm_instance_mgmt_ip': interface_instances[0]['ip_address'],
                                'vm_instance_private_key': vm_instance_keypairs[0]['private_key'],
                                'vm_instance_public_key': vm_instance_keypairs[0]['public_key'],
                                'vm_instance_username': vm_instance_keypairs[0]['username'],
                                'vm_instance_password': vm_instance_keypairs[0]['password']
                            }
                            vnf_instance_graph['vm_instances'].append(vm_instance_graph)
                        scenario_instance_graph['vnf_instances'].append(vnf_instance_graph)
                    scenario_graph['scenario_instances'].append(scenario_instance_graph)
            return scenario_graph
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("scenario_id", str)
    @Out("all_instance_list", str)
    def destroy_all_scenario_instances(self, scenario_id=None):
        """
        This function check if there is any scenario instance available for the specified scenario id
        then it request MaSta for destroying each scenario instance of the scenario and remove
        all entries from Storage related to scenario. If no scenario_id specified it will destroy
        instances of all existing scenario in Storage.

        :param scenario_id: String contains the UUID of the Scenario to be destroyed.
        :return: A python dictionary as string, contains the instances of the specified Scenario
         or of all Scenario. In case of error return the error code as string.
        """
        try:
            all_instance_list = []
            if scenario_id is None:
                # self.logger.debug('Retrieve scenario instances')
                scenarios = self.s.get('scenario', options=[], filters={})
                if len(scenarios) == 0:
                    self.logger.warn("destroy_all_scenario_instances error. There is no scenario available.")
                    return 404
                for scenario in scenarios:
                    scenario_instance_list = self.__delete_scenario_instances__(scenario)
                    all_instance_list.append(scenario_instance_list)
            else:
                # self.logger.debug('Retrieve scenario instances')
                scenarios = self.s.get('scenario', options=[], filters={'uuid': scenario_id})
                if len(scenarios) == 0:
                    self.logger.warn("destroy_all_scenario_instances error. Scenario not found for scenario id %s", scenario_id)
                    return 404

                scenario_instance_list = self.__delete_scenario_instances__(scenarios[0])
                all_instance_list.append(scenario_instance_list)
            return all_instance_list
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __delete_scenario_instances__(self, scenario):
        """
        A private method to retrieve all scenario instance specific to a scenario id and
        request MaSta for destroying each scenario instances of the scenario and remove
        all entry related to scenario instance from the database.
        return a dictionary with of all scenario instances related to the scenario id.

        :param scenario:
        :return:
        """
        scenario_instance_list = {
            'scenario_uuid': scenario['uuid'],
            'scenario_name': scenario['name'],
            'scenario_description': scenario['description'],
            'scenario_instances': []
        }

        scenario_instances = self.s.get('scenario_instance',
                                        options=[],
                                        filters={'scenario_id': scenario['uuid']})
        if len(scenario_instances) == 0:
            self.logger.info("destroy_all_scenario_instances info. There is no scenario instance exist for the scenario %s", scenario['uuid'])
            scenario_instance_list['scenario_instances'].append("There is no scenario instance.")
        else:
            for scenario_instance in scenario_instances:
                self.destroy_scenario_instance(scenario_instance['uuid'])
                scenario_instance_list['scenario_instances'].append(scenario_instance['uuid'])
        return scenario_instance_list

    @In("scenario_instance_id", str)
    @Out("result", str)
    def destroy_scenario_instance(self, scenario_instance_id):
        """
        This function check is the scenario instance exists in Storage and then request MaSta
        for destroying it and if it is successfully destroyed then it remove all entries related
        to scenario instance from the Storage. It calls VNFM Adapter to stop all related VNF Manager
        and Element manager.

        :param scenario_instance_id: String contains the UUID of the Scenario Instance to be destroyed.
        :return: Success code (200)for successful destruction of the Scenario Instance.
         In case of error return the error code as string.
        """
        try:
            if scenario_instance_id is None:
                return 200
            scenario_instance = self.s.get('scenario_instance',
                                           options=[], filters={'uuid': scenario_instance_id})

            if len(scenario_instance) == 0:
                self.logger.warn("destroy_scenario_instance error. Scenario Instance not found")
                return 404

            # scenario_instance_id.replace("-","")

            result = self.rpc.callSync(60, 'decaf_masta.destroy_scenario',
                                       scenario_instance_id=scenario_instance_id)
            if result == 0:
                self.logger.error("destroy_scenario_instance error. Error in decaf_masta module: %r", result)
                return result

            self.__delete_all_instances__(scenario_instance_id)

            # update RPC
            result = self.rpc.callSync(60, 'decaf_vnf_manager_adapter.update')

            self.logger.info("destroy_scenario_instance info. Scenario Instance deleted successfully")

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("scenario_instance_id", str)
    @In("action", str)
    @Out("result", str)
    def scenario_instance_action(self, scenario_instance_id, action):
        """
        This function is used to execute an action on a running scenario instance.
        The same action will be performed on all VM in the scenario, the supported actions are
        start, stop, hard-reboot, soft-reboot, pause, unpause, suspend, resume, shelve, unshelve.

        :param scenario_instance_id: String contains the UUID of the Scenario Instance.
        :param action: String to specify the action.
        :return: Success code (200)for successful execution of the action in MaSta.
         In case of error return the error code as string.
        """
        self.logger.debug("Checking that the instance_id exists and getting the instance dictionary")
        try:
            scenario_instance = self.s.get('scenario_instance', options=[],
                                           filters={'uuid': scenario_instance_id})
            if len(scenario_instance) == 0:
                self.logger.warn("scenario_instance_action error. Scenario Instance not found")
                return 404

            result = self.rpc.callSync(60, 'decaf_masta.action_scenario',
                                        scenario_action = {
                                            "scenario_action": {
                                                "scenario_instance_id": scenario_instance_id,
                                                "action": action
                                            }
                                        })
            if not result:
                self.logger.error("scenario_instance_action error. Error in decaf_masta module: %r", result)
                return result

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("scenario_net_instance_id", str)
    @Out("result", str)
    def delete_scenario_net_instance(self, scenario_net_instance_id):
        """
        This function check if the scenario net instance exists in the Storage
        and then delete all the scenario interface instance, interface instance
        related to scenario net instance and the scenario net instance from Storage.

        :param scenario_net_instance_id: String contains the UUID of the Scenario Net Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            scenario_net_instance = self.s.get('scenario_net_instance', options=[],
                                               filters={'uuid': scenario_net_instance_id})

            if len(scenario_net_instance) == 0:
                self.logger.warn("delete_scenario_net_instance error. Scenario Net Instance not found")
                return 404

            scenario_interface_instances = self.s.get('scenario_interface_instance',
                                                      options=[],
                                                      filters={'scenario_net_instance_id': scenario_net_instance_id})
            for scenario_interface_instance in scenario_interface_instances:
                self.s.delete('scenario_interface_instance',
                              uuid=scenario_interface_instance['uuid'])
                self.s.delete('interface_instance',
                              uuid=scenario_interface_instance['interface_instance_id'])
            self.s.delete('scenario_net_instance',
                          uuid=scenario_net_instance_id)

            self.logger.info("delete_scenario_net_instance info. Scenario Net Instance deleted successfully")

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("net_instance_id", str)
    @Out("result", str)
    def delete_net_instance(self, net_instance_id):
        """
        This function check if the net instance exists in the Storage and then delete all
        the interface instance related to net instance and the net instance from the Storage.

        :param net_instance_id: String contains the UUID of the Net Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            net_instance = self.s.get('net_instance',
                                      options=[], filters={'uuid': net_instance_id})

            if len(net_instance) == 0:
                self.logger.warn("delete_net_instance error. Net Instance not found")
                return 404

            interface_instances = self.s.get('interface_instance',
                                             options=[],
                                             filters={'net_instance_id': net_instance_id})
            for interface_instance in interface_instances:
                self.s.delete('interface_instance',
                              uuid=interface_instance['uuid'])
            self.s.delete('net_instance',
                          uuid=net_instance_id)

            self.logger.info("delete_net_instance info. Net Instance deleted successfully")

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("interface_instance_id", str)
    @Out("result", str)
    def delete_interface_instance(self, interface_instance_id):
        """
        This function check if the interface instance exists in Storage and then delete all
        the interface instance and the scenario interface instance from the Storage.

        :param interface_instance_id: String contains the UUID of the Interface Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            interface_instances = self.s.get('interface_instance',
                                             options=[], filters={'uuid': interface_instance_id})

            if len(interface_instances) == 0:
                self.logger.warn("delete_interface_instance error. Interface Instance not found")
                return 404

            for interface_instance in interface_instances:
                scenario_interface_instances = self.s.get('scenario_interface_instance', options=[],
                                                          filters={'interface_instance_id': interface_instance['uuid']})
                for scenario_interface_instance in scenario_interface_instances:
                    self.delete_scenario_interface_instance(scenario_interface_instance['uuid'])
                self.s.delete('interface_instance',
                              uuid=interface_instance_id)

            self.logger.info("delete_interface_instance info. Scenario Interface Instance deleted successfully")

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("scenario_interface_instance_id", str)
    @Out("result", str)
    def delete_scenario_interface_instance(self, scenario_interface_instance_id):
        """
        This function check if the scenario interface instance exists in Storage and then delete all
        the interface instance and the scenario interface instance from the Storage.

        :param scenario_interface_instance_id: String contains the UUID of the Scenario Interface Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            scenario_interface_instances = self.s.get('scenario_interface_instance', options=[],
                                                      filters={'uuid': scenario_interface_instance_id})

            if len(scenario_interface_instances) == 0:
                self.logger.warn("delete_scenario_interface_instance error. Scenario Interface Instance not found")
                return 404

            for scenario_interface_instance in scenario_interface_instances:
                self.s.delete('scenario_interface_instance',
                              uuid=scenario_interface_instance['uuid'])
                self.s.delete('interface_instance',
                              uuid=scenario_interface_instance['interface_instance_id'])

            self.logger.info("delete_scenario_interface_instance info. Scenario Interface Instance deleted successfully")

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("vm_instance_id", str)
    @Out("result", str)
    def delete_vm_instance(self, vm_instance_id):
        """
        This function check if the VM instance exists in Storage and then delete all
        the interface instance, scenario interface instance and the vm instance and its key pairs
        from the Storage.

        :param vm_instance_id: String contains the UUID of the VM Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            vm_instances = self.s.get('vm_instance',
                                      options=[],
                                      filters={'uuid': vm_instance_id})
            if len(vm_instances) == 0:
                self.logger.warn("delete_vm_instance error. VM Instance not found")
                return 404

            for vm_instance in vm_instances:
                interface_instances = self.s.get('interface_instance',
                                                 options=[],
                                                 filters={'vm_instance_id': vm_instance['uuid']})
                for interface_instance in interface_instances:
                    self.delete_interface_instance(interface_instance['uuid'])
                vm_instance_keypairs = self.s.get('vm_instance_keypair',
                                                  options=[],
                                                  filters={'vm_instance_id': vm_instance['uuid']})
                for vm_instance_keypair in vm_instance_keypairs:
                    self.s.delete('vm_instance_keypair',
                                  uuid=vm_instance_keypair['uuid'])
                self.s.delete('vm_instance',
                              uuid=vm_instance['uuid'])
            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("vnf_instance_id", str)
    @Out("result", str)
    def delete_vnf_instance(self, vnf_instance_id):
        """
        This function check if the VNF instance exists in Storage and then delete all
        the interface instance, scenario interface instance, net instance, vm instance and
        vnf instance from the Storage.

        :param vnf_instance_id: String contains the UUID of the VM Instance.
        :return: Success code (200) for successful deletion.
         In case of error return the error code as string.
        """
        try:
            vnf_instances = self.s.get('vnf_instance',
                                       options=[],
                                       filters={'uuid': vnf_instance_id})
            if len(vnf_instances) == 0:
                self.logger.warn("delete_vnf_instance error. VNF Instance not found")
                return 404

            for vnf_instance in vnf_instances:
                scenario_interface_instances = self.s.get('scenario_interface_instance',
                                                          options=[],
                                                          filters={'vnf_instance_id': vnf_instance['uuid']})
                for scenario_interface_instance in scenario_interface_instances:
                    self.delete_scenario_interface_instance(scenario_interface_instance['uuid'])
                net_instances = self.s.get('net_instance',
                                           options=[],
                                           filters={'vnf_instance_id': vnf_instance['uuid']})
                for net_instance in net_instances:
                    self.delete_net_instance(net_instance['uuid'])
                vm_instances = self.s.get('vm_instance',
                                          options=[],
                                          filters={'vnf_instance_id': vnf_instance['uuid']})
                for vm_instance in vm_instances:
                    self.delete_vm_instance(vm_instance['uuid'])
                self.s.delete('vnf_instance',
                              uuid=vnf_instance['uuid'])

            return 200
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __delete_all_instances__(self, scenario_instance_id):
        """
        Local method to delete all scenario/vnf/vm instances from database
        for a specific scenario instance id

        :param scenario_instance_id:
        :return: Nothing
        """
        try:
            vnf_instances = self.s.get('vnf_instance',
                                       options=[],
                                       filters={'scenario_instance_id': scenario_instance_id})

            for vnf_instance in vnf_instances:
                scenario_interface_instances = self.s.get('scenario_interface_instance',
                                                          options=[],
                                                          filters={'vnf_instance_id': vnf_instance['uuid']})
                for scenario_interface_instance in scenario_interface_instances:
                    self.s.delete('scenario_interface_instance',
                                  uuid=scenario_interface_instance['uuid'])
                    # delete all the interface related to scenario net
                    self.s.delete('interface_instance',
                                  uuid=scenario_interface_instance['interface_instance_id'])

                net_instances = self.s.get('net_instance',
                                           options=[],
                                           filters={'vnf_instance_id': vnf_instance['uuid']})
                for net_instance in net_instances:
                    interface_instances = self.s.get('interface_instance',
                                                     options=[],
                                                     filters={'net_instance_id': net_instance['uuid']})
                    # delete all the interface related to net instance
                    # (it is internal connection inside the VNF)
                    for interface_instance in interface_instances:
                        self.s.delete('interface_instance',
                                      uuid=interface_instance['uuid'])
                    self.s.delete('net_instance',
                                  uuid=net_instance['uuid'])
                scenario_net_instances = self.s.get('scenario_net_instance',
                                                    options=[],
                                                    filters={'scenario_instance_id': scenario_instance_id})
                for scenario_net_instance in scenario_net_instances:
                    self.s.delete('scenario_net_instance',
                                  uuid=scenario_net_instance['uuid'])

                vm_instances = self.s.get('vm_instance',
                                          options=[],
                                          filters={'vnf_instance_id': vnf_instance['uuid']})
                for vm_instance in vm_instances:
                    # delete all the interface which are public port
                    # i.e. connection coming in the scenario or going out of the scenario
                    interface_instances = self.s.get('interface_instance',
                                                     options=[],
                                                     filters={'vm_instance_id': vm_instance['uuid']})
                    for interface_instance in interface_instances:
                        self.s.delete('interface_instance',
                                      uuid=interface_instance['uuid'])
                    vm_instance_keypairs = self.s.get('vm_instance_keypair',
                                                      options=[],
                                                      filters={'vm_instance_id': vm_instance['uuid']})
                    for vm_instance_keypair in vm_instance_keypairs:
                        self.s.delete('vm_instance_keypair',
                                      uuid=vm_instance_keypair['uuid'])
                    self.s.delete('vm_instance',
                                  uuid=vm_instance['uuid'])
                self.s.delete('vnf_instance',
                              uuid=vnf_instance['uuid'])
            self.s.delete('scenario_instance',
                          uuid=scenario_instance_id)
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __get_datacenter__(self, placement_graph, scenario_vnf):
        """
        Local method to retrieve the datacenter details from the placement graph

        :param placement_graph:
        :param scenario_vnf:
        :return: datacenter details specific to the vnf
        """
        return placement_graph  # TODO remove when placement will work with round-robin
        try:
            datacenter = None
            for key in placement_graph.keys():
                if scenario_vnf['vnf_id'] == placement_graph[key]['uuid']:
                    datacenter = placement_graph[key]
                    break

            return datacenter
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __get_vm_instance__(self, vm_instances):
        """
        Local method to search and retrieve the proper vm instance.

        :param vm_instances:
        :return: the vm instance when the uuid matches in both the list
        """
        try:
            vm_instance = None
            for vm_instance1 in vm_instances:
                for vm_instance2 in self.vm_instance_list:
                    # self.logger.debug("vm_instance1 : %s", json.dumps(vm_instance1, indent=4))
                    # self.logger.debug("vm_instance2 : %s", json.dumps(vm_instance2, indent=4))
                    if vm_instance1['uuid'] == vm_instance2:
                        vm_instance = vm_instance1
                        break

            return vm_instance
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __get_vm_instance_id__(self, vm_instances):
        """
        Local method to search and retrieve the proper vm instance.

        :param vm_instances:
        :return: the vm instance id when the uuid matches in both the list
        """
        try:
            vm_instance = None
            for vm_instance1 in vm_instances:
                for vm_instance2 in self.vm_instance_list:
                    # self.logger.debug("vm_instance1 : %s", json.dumps(vm_instance1, indent=4))
                    # self.logger.debug("vm_instance2 : %s", json.dumps(vm_instance2, indent=4))
                    if vm_instance1['uuid'] == vm_instance2:
                        vm_instance = vm_instance1
                        break

            return vm_instance['uuid']
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __get_vnf_instance_id__(self, vnf_instances):
        """
        Local method to search and retrieve the proper vnf instance
        :param vnf_instances:
        :return: the vnf instance id when the uuid matches in both the list
        """
        try:
            vnf_instance = None
            for vnf_instance1 in vnf_instances:
                for vnf_instance2 in self.vnf_instance_list:
                    # self.logger.debug("vnf_instance1 : %s", json.dumps(vnf_instance1, indent=4))
                    # self.logger.debug("vnf_instance2 : %s", json.dumps(vnf_instance2, indent=4))
                    if vnf_instance1['uuid'] == vnf_instance2:
                        vnf_instance = vnf_instance1
                        break

            return vnf_instance['uuid']
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __populate_nodes__(self, scenario_instance):
        """
        This function populates the nodes information into the deployment graph,
        its create the vnf_instance, vm_instance and the net_instance (if there is any
        internal connection between VM inside a VNF). I lso create datacenter_image and
        datacenter_flavor if the corresponding image or flavor associated to the vm does
        not exist in MaSta/Storage.

        :param scenario_instance:
        :return:
        """
        result = 200
        try:
            self.logger.debug("Get the placement graph calling placement component")
            placement_graph = self.rpc.callSync(60, 'decaf_placement.place', scenario_instance['scenario_id'])
            # self.logger.debug("PLACEMENT GRAPH: %s", json.dumps(placement_graph, indent=4))

            # self.logger.debug('Retrieve scenario VNF and VM')
            scenario_vnfs_vms = self.s.get('scenario',
                                           options=[
                                               'scenario_vnfs.vnf.vms.interfaces'
                                           ],
                                           filters={'uuid': scenario_instance['scenario_id']})
            # self.logger.debug("SCENARIO_VNFS_VMS_INTERFACES : %s", json.dumps(scenario_vnfs_vms, indent=4))

            for scenario_vnfs_vm in scenario_vnfs_vms:
                scenario_vnfs = scenario_vnfs_vm['scenario_vnfs']
                # self.logger.debug("SCE_VNF : %s", json.dumps(scenario_vnfs, indent=4))
                for scenario_vnf in scenario_vnfs:
                    datacenter = self.__get_datacenter__(placement_graph, scenario_vnf)
                    # self.logger.debug("DATACENTER : %s", json.dumps(datacenter, indent=4))
                    vnf = scenario_vnf['vnf']
                    # self.logger.debug("VNF : %s", json.dumps(vnf, indent=4))
                    vnf_instance = {
                        'name': vnf['name'],
                        'description': vnf['description'],
                        'vnf_id': vnf['uuid'],
                        'scenario_instance_id': scenario_instance['uuid'],
                        'datacenter_id': datacenter['uuid']
                    }
                    vnf_instance_id = self.s.add('vnf_instance', data=vnf_instance)
                    self.vnf_instance_list.append(vnf_instance_id)

                    vms = vnf['vms']
                    # self.logger.debug("VMS : %s", json.dumps(vms, indent=4))
                    for vm in vms:
                        # self.logger.debug("VM: %s", json.dumps(vm, indent=4))
                        vm_instance = {
                            'name': vm['name'],
                            'description': vm['description'],
                            'vnf_instance_id': vnf_instance_id,
                            'vm_id': vm['uuid']
                        }
                        vm_instance_id = self.s.add('vm_instance', data=vm_instance)
                        self.vm_instance_list.append(vm_instance_id)

                        result = self.deploy_datacenter_image(vm['image_id'], vm['image_path'], datacenter['uuid'])
                        if result != 200:
                            self.logger.error("deploy_scenario error. IMAGE creation failed",
                                              vm['image_id'])
                            self.destroy_scenario_instance(self.current_scenario_instance)
                            return result

                        result = self.deploy_datacenter_flavor(vm['flavor_id'], datacenter['uuid'])
                        if result != 200:
                            self.logger.error("deploy_scenario error. FLAVOR creation failed: <%s>",
                                              vm['flavor_id'])
                            self.destroy_scenario_instance(self.current_scenario_instance)
                            return result

                        # Data needed for preparing deployment graph
                        mgmt = ""
                        interfaces = vm['interfaces']
                        # self.logger.debug("INTERFACES : %s", json.dumps(interfaces, indent=4))
                        for interface in interfaces:
                            # self.logger.debug("INTERFACE: %s", json.dumps(interface, indent=4))
                            if interface['type'] == 'mgmt':
                                mgmt = interface['external_name']
                                break

                        node = {
                            'vm_instance_id': vm_instance_id,
                            'vnf_instance_id': vnf_instance_id,
                            'name': vm['name'],
                            'metadata': {
                                'datacenter': datacenter['datacenter_masta_id'],
                                'image': vm['image_id'],
                                'flavor': vm['flavor_id'],
                                'mgmt': mgmt
                                # ,                           #testing
                                # 'mgmt_physical': mgmt,      #testing
                                # 'mgmt_ip': "192.170.0.1",   #testing
                                # 'keypair': {                #testing
                                #     'keypair_id': 1,        #testing
                                #     'private_key': "blabla",#testing
                                #     'public_key': "blabla", #testing
                                #     'fingerprint': "blub"   #testing
                                # }                           #testing
                            }
                        }
                        self.deploy_graph['graph']['nodes'].append(node)

                    # Adding net instance and interface instance corresponding to vnf
                    # these are internal connections inside a VNF
                    nets = self.s.get('net', options=[], filters={'vnf_id': vnf['uuid']})
                    if len(nets) == 0:
                        self.logger.info("deploy_scenario info. There is no Net in this scenario")
                    else:
                        self.__prepare_net_instance__(nets, vnf_instance_id)
            return result
        except BaseException, e:
            self.logger.error(e)
            return e

    @In("image_id", str)
    @In("image_path", str)
    @In("datacenter_id", str)
    @Out("result", str)
    def deploy_datacenter_image(self, image_id, image_path, datacenter_id):
        """
        This function check if the image already deployed in the MaSta querying the datacenter_images
        table in Storage. It prepare image_data and call MaSta to deploy it in the datacenter. Insert a
        record into the datacenter_images table to mark the image already deployed.

        :param image_id: String contains the UUID of the Image.
        :param image_path: String contains the path to looks for the Image.
        :param datacenter_id: String contains the UUID of the Datacenter, where the Image will be deployed.
        :return: Success code (200) for successful deployment.
         In case of error return the error code as string.
        """
        try:
            # check if the datacenter image already exist
            datacenter_images = self.s.get('datacenter_image',
                                           options=[],
                                           filters={
                                               'image_id': image_id,
                                               'datacenter_id': datacenter_id
                                           })

            if len(datacenter_images) == 0:  # No data found
                # create image at MaSta in case it does not exist
                images = self.s.get('image', options=[],
                                    filters={'uuid': image_id})
                image = images[0]

                datacenters = self.s.get('datacenter', options=[],
                                         filters={'uuid': datacenter_id})
                datacenter = datacenters[0]

                image_data = {
                    'image': {
                        'image_id': image['uuid'],
                        'name': image['name'],
                        'description': image['description'],
                        'url': image_path,
                        'datacenter_id': datacenter['datacenter_masta_id']
                    }
                }
                # self.logger.debug("IMAGE: %s", json.dumps(image_data, indent=4))

                self.logger.debug("Creating Image on MaSta")

                result = self.rpc.callSync(500, 'decaf_masta.create_image', image_data=image_data)
                # result = 200  # testing
                # Either we get the MaSta image_id or the error message in case of failure,
                #  so inform what ever we get from the MaSta
                self.logger.info("deploy_datacenter_image deploying image id : <%s>, MaSta return code : <%s>",
                                 image['uuid'],
                                 result)
                if (result != 200) and (result != 201):
                    self.logger.error("deploy_datacenter_image error. IMAGE creation failed in MaSta image id: <%s>",
                                      image['uuid'])
                    return result

                # Add datacenter image if image creation in MaSta succeeded
                datacenter_image = {
                    'image_id': image['uuid'],
                    'datacenter_id': datacenter['uuid'],
                    'meta': image['meta'],
                    'name': image['name'],
                    'description': image['description'],
                    'masta_image_id': datacenter['datacenter_masta_id']
                }
                self.s.add('datacenter_image', data=datacenter_image)
            else:
                self.logger.info("deploy_datacenter_image info. The image already deployed: <%s>", image_id)

            return 200

        except BaseException, e:
            self.logger.error(e)
            raise e

    @In("flavor_id", str)
    @In("datacenter_id", str)
    @Out("result", str)
    def deploy_datacenter_flavor(self, flavor_id, datacenter_id):
        """
        This function check if the flavor already deployed in the MaSta querying the datacenter_images
        table in Storage. It prepare flavor_data and call MaSta to deploy it in the datacenter. Insert a
        record into the datacenter_flavors table to mark the flavor already deployed.

        :param flavor_id: String contains the UUID of the Flavor.
        :param datacenter_id: String contains the UUID of the Datacenter, where the Flavor will be deployed.
        :return: Success code (200) for successful deployment.
         In case of error return the error code as string.
        """
        try:
            # check if the datacenter flavor already exist
            datacenter_flavors = self.s.get('datacenter_flavor',
                                            options=[],
                                            filters={
                                                'flavor_id': flavor_id,
                                                'datacenter_id': datacenter_id
                                            })
            if len(datacenter_flavors) == 0:  # No data found
                # create flavor at MaSta in case it does not exist
                flavors = self.s.get('flavor', options=[],
                                     filters={'uuid': flavor_id})
                flavor = flavors[0]

                datacenters = self.s.get('datacenter', options=[],
                                         filters={'uuid': datacenter_id})
                datacenter = datacenters[0]

                self.logger.debug("Creating flavor on MaSta")
                flavor_data = {
                    'flavor': {
                        'flavor_id': flavor['uuid'],
                        'name': flavor['name'],
                        'description': flavor['description'],
                        'ram': flavor['ram'],
                        'vcpus': flavor['vcpus'],
                        'disk': flavor['disk'],
                        'datacenter_id': datacenter['datacenter_masta_id']
                    }
                }
                result = self.rpc.callSync(60, 'decaf_masta.create_flavor', flavor_data=flavor_data)
                # result = 200  # testing

                # Either we get the MaSta flavor_id or the error message in case of failure,
                #  so inform what ever we get from the MaSta
                self.logger.info("deploy_datacenter_flavor deploying flavor id : <%s>, MaSta return code : <%s>",
                                 flavor['uuid'],
                                 result)
                if (result != 200) and (result != 201):
                    self.logger.error("deploy_datacenter_flavor error. FLAVOR creation failed in MaSta flavor id: <%s>",
                                      flavor['uuid'])
                    return result

                # Add datacenter flavor if flavor creation in MaSta succeeded
                datacenter_flavor = {
                    'flavor_id': flavor['uuid'],
                    'datacenter_id': datacenter['uuid'],
                    'meta': flavor['meta'],
                    'name': flavor['name'],
                    'description': flavor['description'],
                    'masta_flavor_id': datacenter['datacenter_masta_id']
                }
                self.s.add('datacenter_flavor', data=datacenter_flavor)
            else:
                self.logger.info("deploy_datacenter_flavor info. The flavor already deployed: <%s>", flavor_id)

            return 200

        except BaseException, e:
            self.logger.error(e)
            raise e

    def __populate_edges__(self, scenario_instance):
        """
        Popuplate the edges (connection between the VM) of scenario
        and the public_ports (interface for outside).

        :param scenario_instance:
        :return:
        """
        try:
            self.logger.debug("Retrieve scenario nets")
            scenario_nets = self.s.get('scenario_net', options=[],
                                       filters={'scenario_id': scenario_instance['scenario_id']})
            for scenario_net in scenario_nets:
                scenario_net_instance = {
                    'name': scenario_net['name'],
                    'description': scenario_net['description'],
                    'scenario_net_id': scenario_net['uuid'],
                    'scenario_instance_id': scenario_instance['uuid'],
                    'type': scenario_net['type']
                }
                scenario_net_instance_id = self.s.add('scenario_net_instance', data=scenario_net_instance)

                edge = {
                    'metadata': {}
                }

                self.logger.debug("Retrieve scenario interfaces of net")
                scenario_interfaces = self.s.get('scenario_interface',
                                                 options=[],
                                                 filters={'scenario_net_id': scenario_net['uuid']})
                no_of_interface = 0  # To mark one interface as source and other one as target
                for scenario_interface in scenario_interfaces:
                    no_of_interface += 1

                    # Add interface_instance here
                    interfaces = self.s.get('interface',
                                            options=[],
                                            filters={'uuid': scenario_interface['interface_id']})

                    interface = interfaces[0]

                    vm_instances = self.s.get('vm_instance',
                                              options=[],
                                              filters={'vm_id': interface['vm_id']})

                    vm_instance_id = self.__get_vm_instance_id__(vm_instances)

                    interface_instance = {
                        'name': interface['name'],
                        'description': interface['description'],
                        'internal_name': interface['internal_name'],
                        'external_name': interface['external_name'],
                        'type': interface['type'],
                        'vpci': interface['vpci'],
                        'bw': interface['bw'],
                        'vm_instance_id': vm_instance_id,
                        # 'net_instance_id': scenario_net_instance_id,
                        'interface_id': interface['uuid']
                    }
                    interface_instance_id = self.s.add('interface_instance', data=interface_instance)
                    # Add scenario_interface_instance here
                    scenario_vnfs = self.s.get('scenario_vnf',
                                               options=[],
                                               filters={'uuid': scenario_interface['scenario_vnf_id']})
                    scenario_vnf = scenario_vnfs[0]

                    vnf_instances = self.s.get('vnf_instance',
                                               options=[],
                                               filters={'vnf_id': scenario_vnf['vnf_id']})
                    vnf_instance_id = self.__get_vnf_instance_id__(vnf_instances)

                    scenario_interface_instance = {
                        'name': scenario_interface['name'],
                        'description': scenario_interface['description'],
                        'vnf_instance_id': vnf_instance_id,
                        'scenario_net_instance_id': scenario_net_instance_id,
                        'interface_instance_id': interface_instance_id,
                        'scenario_interface_id': scenario_interface['uuid']
                    }
                    self.s.add('scenario_interface_instance', data=scenario_interface_instance)

                    self.logger.debug("Retrieve interfaces related to scenario interface")
                    vm_instances = self.s.get('vm_instance',
                                              options=[],
                                              filters={'vm_id': interface['vm_id']})

                    vm_instance = self.__get_vm_instance__(vm_instances)

                    if scenario_interface['public'] == True:
                        edge['type']                              = interface['type']
                        edge['vm_instance_id']                    = vm_instance_id
                        edge['metadata']['internal']              = interface['internal_name']
                        edge['metadata']['external']              = interface['external_name']
                        edge['metadata']['interface_instance_id'] = interface_instance_id
                        # edge['metadata']['port_physical'] = interface['external_name']  #testing
                        # edge['metadata']['port_ip'] = "192.168.0.3"                     #testing
                    else:
                        if no_of_interface == 1:
                            edge['type']                        = interface['type']
                            edge['source']                      = vm_instance['uuid']
                            edge['metadata']['source_internal'] = interface['internal_name']
                            edge['metadata']['source_external'] = interface['external_name']
                            edge['metadata']['source_interface_instance_id'] = interface_instance_id
                            # edge['metadata']['source_port_physical'] = interface['external_name']   #testing
                            # edge['metadata']['source_port_ip'] ="10.0.0.10"                         #testing

                        if no_of_interface == 2:
                            edge['type']                        = interface['type']
                            edge['target']                      = vm_instance['uuid']
                            edge['metadata']['target_internal'] = interface['internal_name']
                            edge['metadata']['target_external'] = interface['external_name']
                            edge['metadata']['target_interface_instance_id'] = interface_instance_id
                #             edge['metadata']['target_port_physical'] = interface['external_name']   #testing
                #             edge['metadata']['target_port_ip'] = "10.0.0.11"                        #testing
                # self.logger.debug("edge : %s", json.dumps(edge, indent=4))
                if no_of_interface == 1:
                    # Add to the public_ports if only one interface is associated to a scenario_net
                    self.deploy_graph['graph']['public_ports'].append(edge)
                else:
                    # Add to the edges if two interface is associated to a scenario_net
                    self.deploy_graph['graph']['edges'].append(edge)
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __update_node_info__(self, nodes):
        """
        Update/insert records into vm_instance_keypair and into interface_instance table
        with received information form MaSta.

        :param nodes:
        :return nothing:
        """
        try:
            for node in nodes:
                vm_instance_id = node['vm_instance_id']

                vm_instances = self.s.get('vm_instance',
                                          options=[],
                                          filters={'uuid': node['vm_instance_id']})
                vm_instance = vm_instances[0]
                interfaces = self.s.get('interface',
                                        options=[],
                                        filters={'vm_id': vm_instance['vm_id'], 'type': 'mgmt'})
                interface = interfaces[0]
                interface_instance = {
                    'name': interface['name'],
                    'description': interface['description'],
                    'internal_name': interface['internal_name'],
                    'external_name': interface['external_name'],
                    'type': interface['type'],
                    'vpci': interface['vpci'],
                    'bw': interface['bw'],
                    'vm_instance_id': vm_instance_id,
                    # 'net_instance_id': None, # because its the global management net
                    'interface_id': interface['uuid'],
                    'physical_name': node['metadata']['mgmt_physical'],
                    'ip_address': node['metadata']['mgmt_ip']
                }
                self.s.add('interface_instance', data=interface_instance)
                vms = self.s.get('vm', options=[],
                                 filters={'uuid': vm_instance['vm_id']})
                images = self.s.get('image', options=[],
                                    filters={'uuid': vms[0]['image_id']})
                vm_instance_keypair = {
                    'vm_instance_id': vm_instance_id,
                    'keypair_id': node['metadata']['keypair']['keypair_id'],
                    'private_key': node['metadata']['keypair']['private_key'],
                    'public_key': node['metadata']['keypair']['public_key'],
                    'fingerprint': node['metadata']['keypair']['fingerprint'],
                    'username': images[0]['username'],
                    'password': images[0]['password']
                }
                self.s.add('vm_instance_keypair', data=vm_instance_keypair)
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __update_edge_info__(self, edges):
        """
        Update the interface_instance table records with the received information from MaSta
        these edges are scenario net interfaces.

        :param edges:
        :return nothing:
        """
        try:
            for edge in edges:
                self.s.update('interface_instance',
                              uuid=edge['metadata']['source_interface_instance_id'],
                              data={
                                  'physical_name': edge['metadata']['source_port_physical'],
                                  'ip_address': edge['metadata']['source_port_ip']
                              })

                self.s.update('interface_instance',
                              uuid=edge['metadata']['target_interface_instance_id'],
                              data={
                                  'physical_name': edge['metadata']['target_port_physical'],
                                  'ip_address': edge['metadata']['target_port_ip']
                              })
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __update_public_port_info__(self, public_ports):
        """
        Update the interface_instance table records with the received information from MaSta
        this public ports are interface to outside/inside scenario.

        :param public_ports:
        :return nothing:
        """
        try:
            for public_port in public_ports:
                self.s.update('interface_instance',
                              uuid=public_port['metadata']['interface_instance_id'],
                              data={
                                  'physical_name': public_port['metadata']['port_physical'],
                                  'ip_address': public_port['metadata']['port_ip']
                              })
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __prepare_net_instance__(self, nets, vnf_instance_id):
        """
        Insert records into net_instance and the corresponding records into interface_instance
        for all connection between VM inside a VNF.

        :param nets:
        :param vnf_instance_id:
        :return nothing:
        """
        try:
            for net in nets:
                net_instance = {
                    'name': net['name'],
                    'description': net['description'],
                    'vnf_instance_id': vnf_instance_id,
                    'net_id': net['uuid']
                }
                net_instance_id = self.s.add('net_instance', data=net_instance)

                for interface in self.s.get('interface', options=[], filters={'net_id': net['uuid']}):
                    vm_instances = self.s.get('vm_instance', options=[], filters={'vm_id': interface['vm_id']})
                    vm_instance_id = self.__get_vm_instance_id__(vm_instances)

                    interface_instance = {
                        'name': interface['name'],
                        'description': interface['description'],
                        'internal_name': interface['internal_name'],
                        'external_name': interface['external_name'],
                        'type': interface['type'],
                        'vpci': interface['vpci'],
                        'bw': interface['bw'],
                        'vm_instance_id': vm_instance_id,
                        'net_instance_id': net_instance_id,
                        'interface_id': interface['uuid']
                    }
                    self.s.add('interface_instance', data=interface_instance)
        except BaseException, e:
            self.logger.error(e)
            raise e

    def __del__(self):
        self.dispose()

    def dispose(self):
        super(Deployment, self).dispose()

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass


def daemon():
    daemonize(Deployment)

if __name__ == "__main__":
    daemon()
