#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

"""
decaf-masta implements all the methods to interact with OpenStack.
"""

import json

from decaf_storage.json_base import StorageJSONEncoder
from decaf_storage import Endpoint

from decaf_utils_components.base_daemon import daemonize
import yaml
import time
import urllib
import sqlalchemy.orm.exc
from sqlalchemy import or_
from decaf_utils_components import BasePlugin, In, Out
import base64
import sys
import math
import traceback
from decaf_masta.components.database.mastadatabase import Database
from decaf_masta.components import mastaagent
from decaf_masta.components.database.datacenter import Datacenter
from decaf_masta.components.database.flavor import Flavor
from decaf_masta.components.database.image import Image
from decaf_masta.components.database.keystone import Keystone
from decaf_masta.components.database.vm_instance import VMInstance
from decaf_masta.components.database.scenario import Scenario
from decaf_masta.components.database.management_network import ManagementNetwork
from decaf_masta.components.database.public_network import PublicNetwork
from decaf_masta.components.database.monitoring_alarm import MonitoringAlarm
from decaf_masta.components.database.management_network import ManagementNetwork
from decaf_masta.components.database.management_port import ManagementPort
from decaf_masta.components.database.internaledge import InternalEdge
from decaf_masta.components.database.public_port import PublicPort
from decaf_masta.components.database.keypair import KeyPair
from decaf_masta.components.database.router import Router
from decaf_masta.components.mastaserver import MastaServer

__author__ = "Kristian Hinnenthal"
__date__ = "$2-feb-2016$"

TMPDIR = "/tmp/decaf/"


class Masta(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(Masta, self).__init__(logger=logger, config=config)

        self.mastaserver_url = self.config["mastaserver"]["url"]

        # Connect to database

        self.logger.info('Connect to database...')
        self.db = Database(self.config["database"])
        self.db.init_db()
        self.logger.info('Connected to database.')

        # Create MaSta server

        self.logger.info('Create MastaServer...')
        port = int(self.config["mastaserver"]["url"].split(":")[1])
        self.server = MastaServer(self, self.logger, port)
        self.server.daemon = True
        self.server.start()
        self.logger.info('Created MastaServer.')

        # Initialize all masta-agents with the correct keystone configurations

        self.masta_agents = {}

        session = self.db.get_session()

        self.datacenters = session.query(Datacenter).all()

        for datacenter in self.datacenters:

            keystone_credentials = session.query(Keystone).filter(Keystone.keystone_id == datacenter.keystone_id).first()
            if keystone_credentials is None:
                self.logger.error("There is no keystone entry for datacenter " + str(datacenter.datacenter_id) + ".")

            self.masta_agents[datacenter.datacenter_id] = mastaagent.MastaAgent(
                logger=self.logger,
                datacenter_id=datacenter.datacenter_id,
                datacenter_name=datacenter.datacenter_name,
                keystone_region=datacenter.keystone_region,
                keystone_url=keystone_credentials.keystone_url,
                keystone_domain_id=keystone_credentials.keystone_domain_id,
                keystone_domain_name=keystone_credentials.keystone_domain_name,
                keystone_project_name=keystone_credentials.keystone_project_name,
                keystone_user=keystone_credentials.keystone_user,
                keystone_pass=keystone_credentials.keystone_pass
            )

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    def _after_connect(self):
        self.rpc.set_json_encoder(StorageJSONEncoder)
        self.storage = Endpoint(self.rpc, self.logger)

        # Check if all the datacenters are also registered in Storage, if not, register them

        storage_datacenters = self.storage.get('datacenter', options=[], filters={})

        for datacenter in self.datacenters:
            datacenter_id = datacenter.datacenter_id

            storage_datacenters = self.storage.get('datacenter', options=[], filters={"datacenter_masta_id": datacenter.datacenter_id})

            if len(storage_datacenters) == 0:
                # Datacenter not existent, create in Storage

                self.logger.info("Found datacenter in MaSta database that is not registered in Storage component, registers it...")

                self.storage.add('datacenter', data={
                    "name": datacenter.datacenter_name,
                    "description": "Description created by MaSta.",
                    "type": "openstack",
                    "datacenter_masta_id": datacenter.datacenter_id
                })

                self.logger.info("Datacenter registered.")

    # ----------------------------------------------------------
    # INITIALIZE DATACENTER
    # Initializes the datacenter.
    # ----------------------------------------------------------

    @In("datacenter_id", int)
    @Out("success_code", int)
    def initialize_datacenter(self, datacenter_config):
        """
        Sets up the networks and router for a new datacenter.
        This setup process resembles the process descripted in the documentation of OpenStack Liberty,
        which can be found here: http://docs.openstack.org/liberty/install-guide-ubuntu/launch-instance.html#launch-instance-networks

        :param datacenter_config: A DatacenterConfig object describing the datacenter to be added.
        :return: The id of the new entry.
        """

        self.logger.info("MaSta will now setup datacenter " + str(datacenter_config["datacenter_config"]["datacenter_id"]) + " according to the specification.")

        session = self.db.get_session()

        datacenter_config = datacenter_config["datacenter_config"]
        datacenter_id = datacenter_config["datacenter_id"]
        networks = datacenter_config["networks"]


        # Create the public network

        self.logger.info("Create public network...")

        if session.query(PublicNetwork).filter(PublicNetwork.datacenter_id == datacenter_id).count() > 0:
            # Public network already exists
            public_net_os_id = session.query(PublicNetwork).filter(PublicNetwork.datacenter_id == datacenter_id).first().network_os_id
            new_public_net_created = False
            self.logger.warning("Public network already exists. No public network created.")

        else:
            # No public network exists

            public_net_os_id = self.masta_agents[datacenter_id].create_net({"network": {
                "name": networks["public_network"]["net_name"],
                "admin_state_up": True,
                "shared": True,
                "provider:network_type": "flat",
                "provider:physical_network": "public",
                "router:external": True # This differs from the documentation, in the doc this parameter is inserted later
            }})

            public_net = PublicNetwork(datacenter_id=datacenter_id,
                                       network_os_id=public_net_os_id,
                                       network_os_name=networks["public_network"]["net_name"])
            session.add(public_net)

            public_subnet_os_id = self.masta_agents[datacenter_id].create_subnet({"subnet": {
                "name": networks["public_network"]["subnet_name"],
                "cidr": networks["public_network"]["cidr"],
                "ip_version": networks["public_network"]["ip_version"],
                "network_id": public_net_os_id,
                "allocation_pools": [
                    {
                        "start": networks["public_network"]["allocation_pool"]["start"],
                        "end": networks["public_network"]["allocation_pool"]["end"]
                    }
                ],
                "dns_nameservers": [
                    networks["public_network"]["dns_nameserver"]
                ],
                "gateway_ip": networks["public_network"]["gateway"]
            }})

            public_net.subnetwork_os_id = public_subnet_os_id
            public_net.subnetwork_os_name = networks["public_network"]["subnet_name"]

            new_public_net_created = True
            self.logger.info("Created public network.")

        # Create Management Net

        self.logger.info("Create management network...")

        if session.query(ManagementNetwork).filter(ManagementNetwork.datacenter_id == datacenter_id).count() > 0:
            # Management network already exists
            new_management_net_created = False
            self.logger.warning("Management network already exists. No management network created.")

        else:
            # No management network exists

            mgmt_net_os_id = self.masta_agents[datacenter_id].create_net({"network": {
                "name": networks["management_network"]["net_name"],
                "admin_state_up": True
            }})

            mgmt_net = ManagementNetwork(datacenter_id=datacenter_id,
                                         network_os_id=mgmt_net_os_id,
                                         network_os_name=networks["management_network"]["net_name"])
            session.add(mgmt_net)

            mgmt_subnet_os_id = self.masta_agents[datacenter_id].create_subnet({"subnet": {
                "name": networks["management_network"]["subnet_name"],
                "cidr": networks["management_network"]["cidr"],
                "ip_version": networks["management_network"]["ip_version"],
                "network_id": mgmt_net_os_id,
                "dns_nameservers": [
                    networks["management_network"]["dns_nameserver"]
                ],
                "gateway_ip": networks["management_network"]["gateway"]
            }})

            mgmt_net.subnetwork_os_id = mgmt_subnet_os_id
            mgmt_net.subnetwork_os_name = networks["management_network"]["subnet_name"]

            new_management_net_created = True
            self.logger.info("Created management network.")

        # Create Router

        self.logger.info("Create router...")

        if session.query(Router).filter(Router.datacenter_id == datacenter_id).count() > 0:
            # Router already exists
            router_os_id = session.query(Router).filter(Router.datacenter_id == datacenter_id).first().router_os_id

            new_router_created = False
            self.logger.warning("Router already exists. No router created.")

        else:
            # No router exists
            router_os_id = self.masta_agents[datacenter_id].create_router({"router": {
                "name": datacenter_config["router"]["name"]
            }})

            router = Router(router_os_id=router_os_id,
                            datacenter_id=datacenter_id,
                            router_os_name=datacenter_config["router"]["name"])
            session.add(router)

            new_router_created = True
            self.logger.info("Created router.")


        # Connect Management Network to the router

        if new_management_net_created:
            self.logger.info("Connect management network with router...")
            self.masta_agents[datacenter_id].add_router_interface(mgmt_subnet_os_id, router_os_id)
            self.logger.info("Connected management network with router.")
        else:
            self.logger.info("Assuming management network is already connected with router.")

        # Set the public network as router gateway

        self.logger.info("Set public network as gateway...")

        if new_public_net_created or new_router_created:
            # TODO: find out how exactly the external_fixed_ips object has to look like
            self.masta_agents[datacenter_id].update_router(router_os_id, {"router": {
                "external_gateway_info": {
                    "network_id": public_net_os_id,
                    "enable_snat": "True",
                    "external_fixed_ips": [
                        {
                            "subnet_id": "255.255.255.0",
                            "ip": "192.168.10.1"
                        }
                    ]
                }
            }})

            self.logger.info("Set public network as gateway.")
        else:
            self.logger.info("Assuming public network and router are setup correctly.")

        self.logger.info("Finishing setup...")

        session.commit()

        self.logger.info("Finished setting up datacenter " + str(datacenter_id) + ". MaSta is now ready to work!")


    # ----------------------------------------------------------
    # KEYSTONE
    # There is one set of keystone credentials for each keystone installation.
    # ----------------------------------------------------------

    @In("keystone_credentials", dict)
    @Out("keystone_id", int)
    def create_keystone_credentials(self, keystone_credentials):
        """
        Adds a keystone entry to the database.

        :param keystone_dict: A KeystoneCredentials object containing the new connection data.
        :return: The id of the new entry.
        """

        ks = keystone_credentials["keystone_credentials"]

        session = self.db.get_session()

        keystone = Keystone(keystone_url=ks["keystone_url"],
                            keystone_domain_id=ks["keystone_domain_id"],
                            keystone_domain_name=ks["keystone_domain_name"],
                            keystone_project_name=ks["keystone_project_name"],
                            keystone_user=ks["keystone_user"],
                            keystone_pass=ks["keystone_pass"])
        session.add(keystone)

        session.commit()
        self.logger.info("Created new keystone entry with id " + str(keystone.keystone_id) + ".")

        return int(keystone.keystone_id)

    @In("keystone_id", int)
    @Out("keystone_credentials", dict)
    def get_keystone_credentials(self, keystone_id):
        """
        Gets a keystone entry from the database.

        :param keystone_id: The id of the database entry.
        :return: The data of the keystone entry with the given id, or an error code if not found.
        """

        session = self.db.get_session()
        session.commit()

        keystone = session.query(Keystone).filter(Keystone.keystone_id == keystone_id).first()
        if keystone is not None:
            self.logger.info("Returned keystone entry with id " + str(keystone_id) + ".")
            return keystone.to_dict()
        else:
            self.logger.error("There is no keystone entry with id " + str(keystone_id) + ".")
            return 400

    @Out("keystone_list", list)
    def get_keystones(self):
        """
        Get keystone entries contained in the database.

        :return: A list of keystone entries currently existing in the Masta database.
        """

        session = self.db.get_session()
        session.commit()

        keystones = session.query(Keystone).all()

        return [keystone.to_dict() for keystone in keystones]

    # ----------------------------------------------------------
    # DATACENTERS
    # Every datacenter has a respective set of keystone credentials and a region.
    # Keystone does not have to be installed on the actual datacenter, but could.
    # ----------------------------------------------------------

    @In("datacenter", dict)
    @Out("datacenter_id", int)
    def create_datacenter(self, datacenter):
        """
        Adds a datacenter entry to the database.

        :param datacenter: A Datacenter dictionary containing information of the datacenter.
        :return: The id of the new entry in the database.
        """

        dc = datacenter["datacenter"]

        session = self.db.get_session()
        session.commit()

        datacenter = Datacenter(datacenter_name=dc["datacenter_name"], keystone_id=dc["keystone_id"], keystone_region=dc["keystone_region"])
        session.add(datacenter)

        session.commit()
        self.logger.info("Created new datacenter entry with id " + str(datacenter.datacenter_id) + ".")

        return int(datacenter.datacenter_id)

    @Out("datacenter_list", list)
    def get_datacenters(self):
        """
        Get datacenter entries contained in the database.

        :return: A list of datacenter entries currently existing in the Masta database.
        """

        session = self.db.get_session()

        datacenters = session.query(Datacenter).all()

        self.logger.info("Returned list of all datacenters")
        return [datacenter.to_dict() for datacenter in datacenters]

    @In("datacenter_id", int)
    @Out("datacenter_stats", dict)
    def get_datacenter_stats(self, datacenter_id):
        """
        Returns information about the datacenter.

        :param datacenter_id: The id of the datacenter.
        :return: A list of datacenter entries currently existing in the Masta database
        """

        datacenter_stats = self.masta_agents[datacenter_id].get_datacenter_stats()

        return datacenter_stats

    @In("datacenter_id", int)
    @Out("ip_namespace", str)
    def get_datacenter_ip_namespace(self, datacenter_id):
        """
        Returns the name of the IP namespace of the router on the given datacenter.

        :param datacenter_id: The masta id of the datacenter.
        :return: IP namespace name.
        """

        session = self.db.get_session()

        router = session.query(Router).filter(Router.datacenter_id == datacenter_id).first()
        if router is None:
            self.logger.error("There is no router registered in datacenter " + str(datacenter_id) + ".")
            return 500

        ip_namespace = "qrouter-" + router.router_os_id

        return ip_namespace

    # ----------------------------------------------------------
    # DEPLOY SCENARIO
    # A scenario is deployed in two steps: First, the edges are created.
    # Secondly, the nodes are created.
    # If the process fails at one step, MaSta will rollback the deployment.
    # ----------------------------------------------------------

    @In("instance_graph", dict)
    @Out("instance_graph", dict)
    def deploy_scenario(self, instance_graph):
        """
        Deploy scenario on the infrastructure.

        :param instance_graph: An object of type InstanceGraph to be deployed.
        :return: The modified instance graph with ips and keynames, if successful.
        """

        self.logger.info("Received deploy graph:\n" + json.dumps(instance_graph, indent=4))

        scenario_instance_id = instance_graph["graph"]["scenario_instance_id"]

        self.logger.info("Deploy scenario " + str(scenario_instance_id) + "...")

        session = self.db.get_session()
        session.commit()

        # Create Scenario

        if session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).first() is not None:
            self.logger.error("A scenario with instance id " + str(scenario_instance_id) + " already exists.")
            return 500

        scenario = Scenario(scenario_instance_id=scenario_instance_id)
        session.add(scenario)

        # Create edges

        try:
            self.create_edges(instance_graph, session)
        except Exception, e:
            self.logger.exception("An exception occured.")
            self.rollback(instance_graph, session, del_scenario=True)
            return 500

        # Create nodes

        try:
            self.create_nodes(instance_graph, session)
        except Exception, e:
            self.logger.exception("An exception occured.")
            self.rollback(instance_graph, session, del_scenario=True)
            return 500

        session.commit()

        self.logger.info("Deployed scenario " + str(scenario_instance_id) + ".")

        return instance_graph

    # ----------------------------------------------------------
    # DESTROY SCENARIO
    # Deletes all the nodes and edges and removes
    # the scenario from the database.
    # ----------------------------------------------------------

    @In("scenario_instance_id", str)
    @Out("success_code", int)
    def destroy_scenario(self, scenario_instance_id):
        """
        Destroy scenario by deleting all its nodes and removing from database.

        :param scenario_instance_id: The id of the scenario instance.
        :return: 200, if successful. 404, if not found.
        """

        self.logger.info("Destroy scenario " + str(scenario_instance_id) + "...")

        session = self.db.get_session()
        session.commit()

        if session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).count() == 0:
            self.logger.warning("There is no scenario with id " + str(scenario_instance_id) + ".")
            return 404

        # Delete the nodes

        vm_instance_id_list = [instance.vm_instance_id for instance in session.query(VMInstance).filter(VMInstance.scenario_instance_id == scenario_instance_id).all()]
        if len(vm_instance_id_list) == 0:
            self.logger.info("There are no nodes to delete in scenario " + str(scenario_instance_id) + ".")
        else:
            self.logger.info("Delete nodes of scenario with id " + str(scenario_instance_id) + "...")
            self.delete_nodes(vm_instance_id_list, session)
            self.logger.info("Deleted nodes of scenario with id " + str(scenario_instance_id) + ".")

        # Delete the edges

        # First, collect all the management ports, internal edges and public ports to delete
        edge_list = []
        for edge in session.query(InternalEdge).filter(InternalEdge.scenario_instance_id == scenario_instance_id).all()\
                + session.query(ManagementPort).filter(ManagementPort.scenario_instance_id == scenario_instance_id).all()\
                + session.query(PublicPort).filter(PublicPort.scenario_instance_id == scenario_instance_id).all():
            edge_list.append(edge)

        # Then, delete all the stuff
        if len(edge_list) == 0:
            self.logger.info("There are no edges to delete in scenario " + str(scenario_instance_id) + ".")
        else:
            self.logger.info("Delete edges...")
            self.delete_edges(edge_list, session)
            self.logger.info("Deleted edges.")

        # Delete the scenario
        scenario = session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).one()
        session.delete(scenario)

        session.commit()

        self.logger.info("Destroyed scenario with instance id " + str(scenario_instance_id) + ".")

        return 200

    @Out("success_code", int)
    def destroy_all_scenarios(self):
        """
        Destroys all scenarios in the MaSta database.

        :return: 200, if successful.
        """

        self.logger.info("Destroy all scenarios...")

        session = self.db.get_session()
        session.commit()

        scenario_instance_ids = [scenario.scenario_instance_id for scenario in session.query(Scenario).all()]

        for scenario_instance_id in scenario_instance_ids:
            self.destroy_scenario(scenario_instance_id)

        self.logger.info("Destroyed all scenarios.")

        return 200

    # ----------------------------------------------------------
    # ALTER SCENARIO
    # Methods to change a running scenario.
    # ----------------------------------------------------------

    @In("instance_graph", dict)
    @Out("instance_graph", dict)
    def extend_scenario(self, instance_graph):
        """
        Method to extend an existing scenario.

        :param instance_graph: An InstanceGraph with all the nodes and edges to add.
        :return: 200, if successful.
        """

        scenario_instance_id = instance_graph["graph"]["scenario_instance_id"]

        self.logger.info("Extend scenario " + str(scenario_instance_id) + "...")

        session = self.db.get_session()
        session.commit()

        self.logger.debug(json.dumps(instance_graph, indent=4))

        # Check, if scenario exists

        scenario = session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).first()
        if scenario is None:
            self.logger.error("There is no scenario with instance id " + str(scenario_instance_id) + ".")
            return 500

        # Add edges

        try:
            self.create_edges(instance_graph, session)
        except Exception, e:
            self.logger.error(e)
            self.rollback(instance_graph, session)
            return 500

        # Create nodes

        try:
            self.create_nodes(instance_graph, session)
        except Exception, e:
            self.logger.error(e)
            self.rollback(instance_graph, session)
            return 500

        session.commit()

        self.logger.info("Extended scenario " + str(scenario_instance_id) + ".")

        return instance_graph

    @In("shrink_graph", dict)
    @Out("success_code", int)
    def shrink_scenario(self, shrink_graph):
        """
        Method to shrink an existing scenario.

        :param shrink_graph: An object of type InstanceGraph that lists all the nodes and edges to delete.
        :return: 200, if successful.
        """

        scenario_instance_id = shrink_graph["graph"]["scenario_instance_id"]

        self.logger.info("Shrink scenario " + str(scenario_instance_id) + "...")

        session = self.db.get_session()
        session.commit()

        if session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).count() == 0:
            self.logger.warning("There is no scenario with id " + str(scenario_instance_id) + ".")
            return 404

        # Delete the nodes

        if "nodes" in shrink_graph["graph"]:
            vm_instance_id_list = [node["vm_instance_id"] for node in shrink_graph["graph"]["nodes"]]
            if len(vm_instance_id_list) > 0:
                self.logger.info("Delete nodes...")
                self.delete_nodes(vm_instance_id_list, session)
                self.logger.info("Deleted nodes.")

        # Delete the edges
        # First, collect all the data that needs to be deleted

        edge_list = [] # list that contains db objects of internal edges, management ports and public ports

        # Collect all edges, ports and public ips incident to one of the deleted nodes
        if "nodes" in shrink_graph["graph"]:
            for node in shrink_graph["graph"]["nodes"]:
                edges = session.query(InternalEdge).filter(or_(InternalEdge.source_vm_instance == node["vm_instance_id"], InternalEdge.target_vm_instance == node["vm_instance_id"])).all()

                for edge in edges:
                    if edge not in edge_list:
                        edge_list.append(edge)

                public_ports = session.query(PublicPort).filter(PublicPort.vm_instance_id == node["vm_instance_id"]).all()

                edge_list += public_ports

                management_ports = session.query(ManagementPort).filter(ManagementPort.vm_instance_id == node["vm_instance_id"]).all()

                edge_list += management_ports
        else:
            self.logger.info("No node list given in shrink graph.")

        if "edges" in shrink_graph["graph"]:
            for graph_edge in shrink_graph["graph"]["edges"]:
                edge = session.query(InternalEdge).filter(
                        InternalEdge.scenario_instance_id == scenario_instance_id,
                        InternalEdge.source_interface_instance_id == graph_edge["metadata"]["source_interface_instance_id"],
                        InternalEdge.target_interface_instance_id == graph_edge["metadata"]["target_interface_instance_id"]
                ).first()

                if edge is None:
                    self.logger.error("The edge with source interface uuid " + graph_edge["metadata"]["source_interface_instance_id"] + " to interface id " + graph_edge["metadata"]["target_interface_instance_id"] + " can not be resolved.")
                    return 500

                if edge not in edge_list:
                    edge_list.append(edge)
                else:
                    self.logger.warning("There is an edge specified in the shrink graph that is implicitly deleted anyhow.")
        else:
            self.logger.info("No edge list given in shrink graph.")

        if "public_ports" in shrink_graph["graph"]:
            for public_port in shrink_graph["graph"]["public_ports"]:

                public_port_object = session.query(PublicPort).filter(
                        PublicPort.scenario_instance_id == scenario_instance_id,
                        PublicPort.interface_instance_id == public_port["metadata"]["interface_instance_id"]
                ).first()

                if public_port_object is None:
                    self.logger.error("A public port with interface uuid " + public_port["metadata"]["interface_instance_id"] + " can not be resolved.")
                    return 500

                edge_list.append(public_port)
        else:
            self.logger.info("No public port list given in shrink graph.")

        # Then, delete all the stuff
        self.logger.info("Delete edges...")
        if len(edge_list) > 0:
            self.delete_edges(edge_list, session)
        self.logger.info("Deleted edges.")

        session.commit()

        self.logger.info("Shrunk scenario with instance id " + str(scenario_instance_id) + ".")

        return 200

    # ----------------------------------------------------------
    # INTERNAL SCENARIO METHODS
    # Internal methods for creation and deletion
    # of nodes and edges.
    # ----------------------------------------------------------

    def create_nodes(self, instance_graph, session):
        """
        Internal method to create nodes in database and deploy the nodes on the infrastructure.

        :param instance_graph: The graph of the scenario.
        :param session: The session object.
        :return:
        """

        scenario_instance_id = instance_graph["graph"]["scenario_instance_id"]

        self.logger.info("Create nodes for scenario " + str(scenario_instance_id) + "...")

        if "nodes" in instance_graph["graph"]:
            for node in instance_graph["graph"]["nodes"]:

                vm_instance_id = node["vm_instance_id"]

                self.logger.info("Create node with instance id " + str(vm_instance_id) + "...")

                if "name" in node:
                    node_name = node["name"]
                else:
                    node_name = str(vm_instance_id)

                flavor = session.query(Flavor).filter(Flavor.flavor_id == node["metadata"]["flavor"]).first()
                if flavor is None:
                    raise Exception("There is no flavor with id " + str(node["metadata"]["flavor"]) + ".")

                image = session.query(Image).filter(Image.image_id == node["metadata"]["image"]).first()
                if image is None:
                    raise Exception("There is no image with id " + str(node["metadata"]["image"]) + ".")

                # Create a keypair

                keypair = KeyPair(vm_instance_id=vm_instance_id,
                                  datacenter_id=node["metadata"]["datacenter"])

                session.add(keypair)
                session.flush()

                keypair.name = "keypair-" + str(keypair.keypair_id)
                session.flush()

                os_keypair_info = self.masta_agents[node["metadata"]["datacenter"]].create_keypair(keypair.name)

                node["metadata"]["keypair"] = {
                    "keypair_id": keypair.keypair_id,
                    "private_key": os_keypair_info["keypair"]["private_key"],
                    "public_key": os_keypair_info["keypair"]["public_key"],
                    "fingerprint": os_keypair_info["keypair"]["fingerprint"]
                }

                # Collect the edges of this node and setup a startup script to initialize the edges
                startup_script = "#!/bin/sh\ncat > /etc/network/interfaces <<EOF\n\n"

                # Management edge

                mgmt_port = session.query(ManagementPort).filter(ManagementPort.vm_instance_id == vm_instance_id).first()
                if mgmt_port is None:
                    raise Exception("There is no management port for vm " + str(vm_instance_id) + ".")

                networks = [
                    {
                        "port": mgmt_port.port_os_id
                    }
                ]

                # startup_script += "# MANAGEMENT\n\n# port = " + mgmt_port.port + "\n" \
                #         + "auto " + mgmt_port.physical_port + "\n" \
                #         + "iface " + mgmt_port.physical_port + " inet static\n" \
                #         + "\taddress " + mgmt_port.port_os_ip + "\n" \
                #         + "\tnetmask 255.255.255.0\n\n"

                startup_script += "# MANAGEMENT\n\n# port = " + mgmt_port.port + "\n" \
                        + "auto " + mgmt_port.physical_port + "\n" \
                        + "iface " + mgmt_port.physical_port + " inet dhcp\n\n"

                physical_ports = [mgmt_port.physical_port]

                # Internal edges
                startup_script += "# INTERNAL EDGES\n\n"

                for edge in session.query(InternalEdge).filter((InternalEdge.source_vm_instance == vm_instance_id) | (InternalEdge.target_vm_instance == vm_instance_id)).all():

                    if str(edge.source_vm_instance) == str(vm_instance_id): # node is source of this edge
                        port_os_id = edge.source_os_port_id
                        interface_instance_id = edge.source_interface_instance_id
                        internal = edge.source_internal
                        external = edge.source_external
                        physical_port = edge.source_physical_port
                    elif str(edge.target_vm_instance) == str(vm_instance_id): # node is target of this edge
                        port_os_id = edge.target_os_port_id
                        interface_instance_id = edge.target_interface_instance_id
                        internal = edge.target_internal
                        external = edge.target_external
                        physical_port = edge.target_physical_port
                    else:
                        raise Exception("VM instance with id " + str(vm_instance_id) + " could not be resolved as source " + str(edge.source_vm_instance) + " or target " + str(edge.target_vm_instance) + " of an edge.")

                    physical_ports.append(physical_port)

                    networks.append(
                            {
                                "port": port_os_id
                            })

                    # startup_script += "# relation = " + edge.relation + "\n" \
                    #     + "# port = " + port + "\n" \
                    #     + "auto " + physical_port + "\n" \
                    #     + "iface " + physical_port + " inet static\n" \
                    #     + "\taddress " + ip + "\n" \
                    #     + "\tnetmask 255.255.0.0\n\n"

                    startup_script += "# interface_instance_id = " + interface_instance_id + "\n" \
                        + "# type = " + edge.type + "\n" \
                        + "# internal = " + internal + "\n" \
                        + "# external = " + external + "\n" \
                        + "auto " + physical_port + "\n" \
                        + "iface " + physical_port + " inet dhcp\n\n"

                # Public ports
                startup_script += "# PUBLIC PORTS\n\n"

                for port in session.query(PublicPort).filter(PublicPort.vm_instance_id == vm_instance_id).all():
                    physical_port = port.physical_port
                    physical_ports.append(physical_port)

                    networks.append(
                            {
                                "port": port.port_os_id
                            })

                    # startup_script += "# relation = " + port.relation + "\n" \
                    #         + "# port = " + port.port + "\n" \
                    #         + "auto " + physical_port + "\n" \
                    #         + "iface " + physical_port + " inet static\n" \
                    #         + "\taddress " + port.port_os_ip + "\n" \
                    #         + "\tnetmask 255.255.255.0\n\n"

                    # Get public port IP via dhcp
                    startup_script += "# interface_instance_id = " + port.interface_instance_id + "\n" \
                            + "# type = " + port.type + "\n" \
                            + "# internal = " + port.internal + "\n" \
                            + "# external = " + port.external + "\n" \
                            + "auto " + physical_port + "\n" \
                            + "iface " + physical_port + " inet dhcp\n\n"

                # Tell VM to start all its interfaces
                startup_script += "EOF\n\n"
                for physical_port in physical_ports:
                    startup_script += "ifup " + physical_port + "\n\n"

                # Change the hostname
                startup_script += 'sed -i \'/127\.0\.1\.1/ c\\127\.0\.1\.1\t' + node_name.lower() + '\' /etc/hosts'

                self.logger.debug(startup_script)

                # Summarize the instance data

                instance_data = {
                    "server": {
                        "name": node_name,
                        "imageRef": image.image_os_id,
                        "flavorRef": flavor.flavor_os_id,
                        "networks": networks,
                        "user_data": base64.b64encode(startup_script),
                        "key_name": keypair.name
                    }
                }

                self.logger.debug(json.dumps(instance_data, indent=4))

                vm_os_info = self.masta_agents[int(node["metadata"]["datacenter"])].new_vm_instance(instance_data)

                vminstance = VMInstance(vm_instance_id=vm_instance_id,
                                        datacenter_id=node["metadata"]["datacenter"],
                                        scenario_instance_id=scenario_instance_id,
                                        vm_os_id=vm_os_info["server"]["id"])

                session.add(vminstance)
                session.flush()

                self.logger.info("Created node with instance id " + str(vm_instance_id) + ".")

                time.sleep(3)

        self.logger.info("Created nodes for scenario " + str(scenario_instance_id) + ".")

    def create_edges(self, instance_graph, session):
        """
        Internal method to create edges in the database and set up the networks in OpenStack.

        :param instance_graph: The graph of the scenario.
        :param session: The session object.
        :return:
        """

        scenario_instance_id = instance_graph["graph"]["scenario_instance_id"]

        self.logger.info("Create edges for scenario " + str(scenario_instance_id) + "...")

        # First, create all the management ports for the instances

        if "nodes" in instance_graph["graph"]:
            for node in instance_graph["graph"]["nodes"]:

                management_network = session.query(ManagementNetwork).filter(ManagementNetwork.datacenter_id == node["metadata"]["datacenter"]).first()
                if management_network is None:
                    raise Exception("There is no management network setup in datacenter " + str(node["metadata"]["datacenter"]) + ".")

                port_result = self.masta_agents[node["metadata"]["datacenter"]].create_port(management_network.network_os_id)

                port_os_ip = port_result["port"]["fixed_ips"][0]["ip_address"]

                mgmt_physical_port = "eth0"  # Yep, that's hardcoded.

                node["metadata"]["mgmt_physical"] = mgmt_physical_port
                node["metadata"]["mgmt_ip"] = port_os_ip

                # Create the database object

                mgmt_port = ManagementPort(
                        vm_instance_id=node["vm_instance_id"],
                        port=node["metadata"]["mgmt"],
                        physical_port=mgmt_physical_port,
                        port_os_id=port_result["port"]["id"],
                        port_os_ip=port_os_ip,
                        datacenter_id=node["metadata"]["datacenter"],
                        scenario_instance_id=scenario_instance_id)

                session.add(mgmt_port)

                session.flush()

        # Count the number of already existent internal edges for this scenario
        # At the time of first deployment, this should be 0
        numEdges = session.query(InternalEdge).filter(InternalEdge.scenario_instance_id == scenario_instance_id).count()

        if "edges" in instance_graph["graph"]:
            for edge in instance_graph["graph"]["edges"]:

                # Internal edge. Create a network and
                # lookup source and target nodes.
                source_node = None
                target_node = None
                for node in instance_graph["graph"]["nodes"]:
                    if node["vm_instance_id"] == str(edge["source"]):
                        source_node = node
                        source_datacenter = source_node["metadata"]["datacenter"]
                        source_vm_instance_id = node["vm_instance_id"]
                    if node["vm_instance_id"] == str(edge["target"]):
                        target_node = node
                        target_datacenter = target_node["metadata"]["datacenter"]
                        target_vm_instance_id = node["vm_instance_id"]

                if source_node is None:
                    # Maybe this node already exists?
                    source_node = session.query(VMInstance).filter(VMInstance.vm_instance_id == edge["source"], VMInstance.scenario_instance_id == scenario_instance_id).first()
                    if source_node is None:
                        # Still not there... something wrong!
                        raise Exception("The source node with instance id " + edge["source"] + " could not be resolved.")
                    else:
                        source_datacenter = source_node.datacenter_id
                        source_vm_instance_id = str(source_node.vm_instance_id)

                if target_node is None:
                    # Maybe this node already exists?
                    target_node = session.query(VMInstance).filter(VMInstance.vm_instance_id == edge["target"], VMInstance.scenario_instance_id == scenario_instance_id).first()
                    if target_node is None:
                        # Still not there... something wrong!
                        raise Exception("The target node with instance id " + edge["target"] + " could not be resolved.")
                    else:
                        target_datacenter = target_node.datacenter_id
                        target_vm_instance_id = str(target_node.vm_instance_id)

                if source_datacenter != target_datacenter:
                    raise Exception("Unequal source and target datacenters can't be handled yet.")
                    #TODO: Handle that!
                else:
                    datacenter_id = source_datacenter

                # Generate a cidr, such that every edge has a disjoint address space
                a = int(math.floor(numEdges/256))
                b = int(numEdges%256)
                cidr = "100." + str(a) + "." + str(b) + ".0/24" # 65536 edges are possible

                # Generate the correct physical port names

                source_num_ports = session.query(InternalEdge).filter(or_(InternalEdge.source_vm_instance == source_vm_instance_id, InternalEdge.target_vm_instance == source_vm_instance_id)).count()
                source_num_ports += session.query(PublicPort).filter(PublicPort.vm_instance_id == source_vm_instance_id).count()
                source_physical_port = "eth" + str(source_num_ports+1)

                target_num_ports = session.query(InternalEdge).filter(or_(InternalEdge.source_vm_instance == target_vm_instance_id, InternalEdge.target_vm_instance == target_vm_instance_id)).count()
                target_num_ports += session.query(PublicPort).filter(PublicPort.vm_instance_id == target_vm_instance_id).count()
                target_physical_port = "eth" + str(target_num_ports+1)

                # Create the database object

                edge_db_object = InternalEdge(
                    cidr=cidr,
                    source_vm_instance=edge["source"],
                    source_interface_instance_id=edge["metadata"]["source_interface_instance_id"],
                    source_internal=edge["metadata"]["source_internal"],
                    source_external=edge["metadata"]["source_external"],
                    source_physical_port=source_physical_port,
                    target_vm_instance=edge["target"],
                    target_interface_instance_id=edge["metadata"]["target_interface_instance_id"],
                    target_internal=edge["metadata"]["target_internal"],
                    target_external=edge["metadata"]["target_external"],
                    target_physical_port=target_physical_port,
                    type=edge["type"],
                    datacenter_id=datacenter_id,
                    scenario_instance_id=scenario_instance_id
                )

                session.add(edge_db_object)
                session.flush()

                # Create a network for this edge
                net_name = "edge-" + str(edge_db_object.edge_id) + "-net"
                net_id = self.masta_agents[datacenter_id].create_net({"network": {
                    "name": net_name,
                    "admin_state_up": True
                }})

                # Create a subnet for this edge
                subnet_name = "edge-" + str(edge_db_object.edge_id) + "-subnet"

                subnet_id = self.masta_agents[datacenter_id].create_subnet({
                    "subnet": {
                        "network_id": net_id,
                        "ip_version": 4,
                        "name": subnet_name,
                        "cidr": cidr
                    }
                })

                edge_db_object.network_os_id = net_id
                edge_db_object.network_os_name = net_name
                edge_db_object.subnetwork_os_id = subnet_id
                edge_db_object.subnetwork_os_name = subnet_name

                # Create the two ports

                source_port_result = self.masta_agents[datacenter_id].create_port(edge_db_object.network_os_id)
                edge_db_object.source_os_port_id = source_port_result["port"]["id"]
                edge_db_object.source_vm_ip = source_port_result["port"]["fixed_ips"][0]["ip_address"]
                session.flush()

                target_port_result = self.masta_agents[datacenter_id].create_port(edge_db_object.network_os_id)
                edge_db_object.target_os_port_id = target_port_result["port"]["id"]
                edge_db_object.target_vm_ip = target_port_result["port"]["fixed_ips"][0]["ip_address"]
                session.flush()

                # If source or target vm did already exist, attach them to the network

                tries = 5  # number of attempts to attach the vm to the network
                waiting_time = 10  # seconds until next try

                if isinstance(source_node, VMInstance):
                    response = self.masta_agents[source_node.datacenter_id].attach_vm_to_net(source_node.vm_os_id, edge_db_object.source_os_port_id)
                    while response == 409 and tries > 0:
                        self.logger.warning("Existing VM with instance id " + str(source_node.vm_instance_id) + " is still spawning, can not be attached to new edge. Will try again in " + str(waiting_time) + " seconds. (Attempts left: " + str(tries) + ")")
                        time.sleep(waiting_time)
                        response = self.masta_agents[source_node.datacenter_id].attach_vm_to_net(source_node.vm_os_id, edge_db_object.source_os_port_id)
                        tries -= 1
                    if response == 409:
                        # Still not spawned, raise Error
                        raise Exception("Existing VM with instance id " + str(source_node.vm_instance_id) + " is not spawning in time. It can not be attached to the edge.")

                if isinstance(target_node, VMInstance):
                    response = self.masta_agents[target_node.datacenter_id].attach_vm_to_net(target_node.vm_os_id, edge_db_object.target_os_port_id)
                    while response == 409 and tries > 0:
                        self.logger.warning("Existing VM with instance id " + str(target_node.vm_instance_id) + " is still spawning, can not be attached to new edge. Will try again in " + str(waiting_time) + " seconds. (Attempts left: " + str(tries) + ")")
                        time.sleep(waiting_time)
                        response = self.masta_agents[target_node.datacenter_id].attach_vm_to_net(target_node.vm_os_id, edge_db_object.target_os_port_id)
                        tries -= 1
                    if response == 409:
                        # Still not spawned, raise Error
                        raise Exception("Existing VM with instance id " + str(target_node.vm_instance_id) + " is not spawning in time. It can not be attached to the edge.")

                # Add ip and port information to the graph

                edge["metadata"]["source_port_physical"] = source_physical_port
                edge["metadata"]["source_port_ip"] = edge_db_object.source_vm_ip
                edge["metadata"]["target_port_physical"] = target_physical_port
                edge["metadata"]["target_port_ip"] = edge_db_object.target_vm_ip

                numEdges += 1

        if "public_ports" in instance_graph["graph"]:
            for public_port in instance_graph["graph"]["public_ports"]:

                # Public port. Instead of creating edges, we simply create a port in the public network

                vm_instance_id = public_port["vm_instance_id"]

                for node in instance_graph["graph"]["nodes"]:
                    if node["vm_instance_id"] == vm_instance_id:
                        datacenter = node["metadata"]["datacenter"]

                if datacenter is None:
                    raise Exception("The datacenter of node " + vm_instance_id + " could not be resolved.")

                # Create the port on the public network

                public_network = session.query(PublicNetwork).filter(PublicNetwork.datacenter_id == datacenter).first()
                if public_network is None:
                    raise Exception("There is no public network setup in datacenter " + str(datacenter) + ".")

                port_result = self.masta_agents[datacenter].create_port(public_network.network_os_id)
                port_os_ip = port_result["port"]["fixed_ips"][0]["ip_address"]

                # Generate the correct physical port name

                num_ports = session.query(InternalEdge).filter(or_(InternalEdge.source_vm_instance == vm_instance_id, InternalEdge.target_vm_instance == vm_instance_id)).count()
                num_ports += session.query(PublicPort).filter(PublicPort.vm_instance_id == vm_instance_id).count()
                physical_port = "eth" + str(num_ports+1)

                # Create the database object

                public_port_object = PublicPort(
                        vm_instance_id=vm_instance_id,
                        interface_instance_id=public_port["metadata"]["interface_instance_id"],
                        internal=public_port["metadata"]["internal"],
                        external=public_port["metadata"]["external"],
                        physical_port=physical_port,
                        type=public_port["type"],
                        port_os_id=port_result["port"]["id"],
                        port_os_ip=port_os_ip,
                        datacenter_id=datacenter,
                        scenario_instance_id=scenario_instance_id)

                session.add(public_port_object)

                session.flush()

                # Add ip and port information to graph

                public_port["metadata"]["port_physical"] = physical_port
                public_port["metadata"]["port_ip"] = port_os_ip

        self.logger.info("Created edges for scenario " + str(scenario_instance_id) + ".")

    def rollback(self, instance_graph, session, del_scenario=False):
        """
        Internal method to rollback the creation or altering of a scenario.

        :param instance_graph: The graph of the scenario.
        :param session: The session object.
        :return:
        """

        scenario_instance_id = instance_graph["graph"]["scenario_instance_id"]

        self.logger.warning("Error occurred, rollback started.")

        # Delete the nodes

        if "nodes" in instance_graph["graph"]:
            vm_instance_id_list = [node["vm_instance_id"] for node in instance_graph["graph"]["nodes"]]
        else:
            vm_instance_id_list = []

        if len(vm_instance_id_list) == 0:
            self.logger.info("There are no nodes to delete in scenario " + str(scenario_instance_id) + ".")
        else:
            self.logger.info("Delete nodes of scenario with id " + str(scenario_instance_id) + "...")
            self.delete_nodes(vm_instance_id_list, session)
            self.logger.info("Deleted nodes of scenario with id " + str(scenario_instance_id) + ".")

        time.sleep(4)

        # Delete Edges
        # First, collect all the data that needs to be deleted

        edge_list = [] # list that contains db objects of internal edges, management ports and public ports

        # Management ports
        if "nodes" in instance_graph["graph"]:
            for node in instance_graph["graph"]["nodes"]:
                mgmt_port = session.query(ManagementPort).filter(
                    ManagementPort.scenario_instance_id == scenario_instance_id,
                    ManagementPort.vm_instance_id == node["vm_instance_id"]
                ).first()

                if mgmt_port is None:
                    self.logger.warning("The management port of VM " + str(node["vm_instance_id"]) + " cannot be found in the database, but might have been created in OpenStack.")
                else:
                    edge_list.append(mgmt_port)

        if "edges" in instance_graph["graph"]:
            for graph_edge in instance_graph["graph"]["edges"]:
                # Internal edges
                edge = session.query(InternalEdge).filter(
                        InternalEdge.scenario_instance_id == scenario_instance_id,
                        InternalEdge.source_interface_instance_id == graph_edge["metadata"]["source_interface_instance_id"],
                        InternalEdge.target_interface_instance_id == graph_edge["metadata"]["target_interface_instance_id"]
                ).first()

                if edge is None:
                    self.logger.error("The edge with source interface uuid " + graph_edge["metadata"]["source_interface_instance_id"] + " to interface id " + graph_edge["metadata"]["target_interface_instance_id"] + " can not be found in the database, but might have been created in OpenStack.")
                else:
                    edge_list.append(edge)

        if "public_port" in instance_graph["graph"]:
            for public_port in instance_graph["graph"]["public_ports"]:
                # Public port
                vm_instance_id = public_port["vm_instance_id"]

                public_port_object = session.query(PublicPort).filter(
                        PublicPort.scenario_instance_id == scenario_instance_id,
                        PublicPort.interface_instance_id == public_port["metadata"]["interface_instance_id"]
                ).first()

                if public_port_object is None:
                    self.logger.warning("A public port with interface_instance_id " + public_port["metadata"]["interface_instance_id"] + " can not be found in the database, but might have been created in OpenStack.")
                else:
                    edge_list.append(public_port_object)

        # Then, delete all the stuff
        self.logger.info("Delete edges...")
        if len(edge_list) > 0:
            self.delete_edges(edge_list, session)
        self.logger.info("Deleted edges.")

        session.commit()

        if del_scenario:
            self.logger.info("Delete scenario from database...")

            scenario = session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).first()
            if scenario is not None:
                session.delete(scenario)

            session.commit()

            self.logger.info("Deleted scenario.")

        self.logger.info("Rollback successful.")

    def delete_nodes(self, vm_instance_id_list, session):
        """
        Internal method to delete nodes from a scenario.

        :param scenario_instance_id: The id of the scenario.
        :param session: The session object.
        :return: 200, if successful.
        """

        for vm_instance_id in vm_instance_id_list:

            self.logger.info("Delete node with instance id " + str(vm_instance_id) + "...")

            # Lookup monitoring alarms for this VM and delete them
            monitoring_alarms = session.query(MonitoringAlarm).filter(MonitoringAlarm.vm_instance_id == vm_instance_id).all()
            for monitoring_alarm in monitoring_alarms:
                self.masta_agents[monitoring_alarm.datacenter_id].delete_monitoring_alarm(monitoring_alarm.alarm_os_id)
                session.delete(monitoring_alarm)
                session.flush()

            # Lookup the keypair and delete it
            keypair = session.query(KeyPair).filter(KeyPair.vm_instance_id == vm_instance_id).first()
            if keypair is None:
                self.logger.warning("There is no keypair corresponding to the vm instance with id " + str(vm_instance_id) + " in the database.")
            else:
                self.masta_agents[keypair.datacenter_id].delete_keypair(keypair.name)
                session.delete(keypair)
                session.flush()

            # Lookup the instance and delete
            vm_instance = session.query(VMInstance).filter(VMInstance.vm_instance_id == vm_instance_id).first()
            if vm_instance is None:
                self.logger.warning("There is no vm instance with id " + str(vm_instance_id) + " in the database.")
            else:
                self.masta_agents[vm_instance.datacenter_id].delete_vm_instance(vm_instance.vm_os_id)
                session.delete(vm_instance)
                session.flush()

            self.logger.info("Deleted node with instance id " + str(vm_instance_id) + ".")

        return 200

    def delete_edges(self, edge_list, session):
        """
        Internal method to delete edges from a scenario.

        :param edge_list: A list containing objects of internal edges, management ports and public ports from the db.
        :param session: The session object.
        :return:
        """

        for edge in edge_list:

            if isinstance(edge, ManagementPort):
                port = edge

                self.masta_agents[port.datacenter_id].delete_port(port.port_os_id)

                session.delete(port)

                self.logger.info("Deleted management port with id " + str(port.management_port_id) + ".")

            elif isinstance(edge, InternalEdge):

                # Delete ports
                self.masta_agents[edge.datacenter_id].delete_port(edge.source_os_port_id)
                self.masta_agents[edge.datacenter_id].delete_port(edge.target_os_port_id)

                # Delete networks
                self.masta_agents[edge.datacenter_id].delete_subnet(edge.subnetwork_os_id)

                self.masta_agents[edge.datacenter_id].delete_net(edge.network_os_id)

                # Remove edge from database
                session.delete(edge)

                self.logger.info("Deleted internal edge with type " + str(edge.type) + " from node " + str(edge.source_vm_instance) + " to node " + str(edge.target_vm_instance) + ".")

            elif isinstance(edge, PublicPort):
                port = edge

                self.masta_agents[port.datacenter_id].delete_port(port.port_os_id)

                session.delete(port)

                self.logger.info("Deleted public port with id " + str(port.public_port_id) + ".")

            else:
                raise Exception("There is an edge to delete that can not be identified.")

            session.delete(edge)
            session.flush()

    # ----------------------------------------------------------
    # ACTIONS
    # Perform actions on the VMS.
    # ----------------------------------------------------------

    @In("vm_action", dict)
    @Out("success_code", int)
    def action_vm_instance(self, vm_action):
        """
        Perform an action on a single vm instance.

        :param vm_action: A dictionary of type VMAction containing the vm instance id and the action to perform.
        :return: 200, if successful.
        """

        vm_instance_id = vm_action["vm_action"]["vm_instance_id"]
        action = vm_action["vm_action"]["action"]

        session = self.db.get_session()

        vm_instance = session.query(VMInstance).filter(VMInstance.vm_instance_id == vm_instance_id).first()

        if vm_instance is None:
            self.logger.error("There is no VM registered under instance id" + str(vm_instance_id) + ".")
            return 404
        else:
            self.masta_agents[vm_instance.datacenter_id].action_vm_instance(vm_instance.vm_os_id, action)

            self.logger.info("Performed action " + str(action) + " on VM " + str(vm_instance_id) + ".")

            return 200

    @In("scenario_action", dict)
    @Out("success_code", int)
    def action_scenario(self, scenario_action):
        """
        Perform an action on a scenario.

        :param scenario_action: A dictionary of type ScenarioAction containing the scenario instance id and the action to perform.
        :return: 200, if successful.
        """

        scenario_instance_id = scenario_action["scenario_action"]["scenario_instance_id"]
        action = scenario_action["scenario_action"]["action"]

        session = self.db.get_session()

        # Check, if scenario exists

        scenario = session.query(Scenario).filter(Scenario.scenario_instance_id == scenario_instance_id).first()
        if scenario is None:
            self.logger.error("There is no scenario with instance id " + str(scenario_instance_id) + ".")
            return 404

        # Gather VMs

        vm_instances = session.query(VMInstance).filter(VMInstance.scenario_instance_id == scenario_instance_id).all()

        for vm_instance in vm_instances:

            self.masta_agents[vm_instance.datacenter_id].action_vm_instance(vm_instance.vm_os_id, action)

        self.logger.info("Performed action " + str(action) + " on scenario " + str(scenario_instance_id) + ".")

        return 200

    # ----------------------------------------------------------
    # FLAVORS
    # ----------------------------------------------------------

    @In("flavor_data", dict)
    @Out("success_code", int)
    def create_flavor(self, flavor_data):
        """
        Adds a flavor entry to the database and uploads the flavor to OpenStack.

        :param flavor_data: A FlavorData object containing data about the flavor.
        :return: 201: flavor created. 200: flavor already exists, not created
        """

        self.logger.info("Create new flavor...")

        session = self.db.get_session()

        flavor_data = flavor_data["flavor"]

        #self.logger.debug("flavor_id given " + flavor_data["flavor_id"])
        #self.logger.debug(session.query(Flavor).filter(Flavor.flavor_id == flavor_data["flavor_id"]).all())

        if session.query(Flavor).filter(Flavor.flavor_id == flavor_data["flavor_id"]).first() is not None:
            self.logger.warning("A flavor with id " + str(flavor_data["flavor_id"]) + " already exists in the MaSta database.")
            return 200
        else:
            os_flavor_id = self.masta_agents[int(flavor_data["datacenter_id"])].create_flavor(flavor_data)

            flavor = Flavor(flavor_id=flavor_data["flavor_id"],
                            datacenter_id=flavor_data["datacenter_id"],
                            flavor_os_id=os_flavor_id,
                            description=flavor_data["description"])
            session.add(flavor)

            session.commit()

            self.logger.info("Created new flavor with id " + str(flavor.flavor_id) + ".")

            return 201

    @In("flavor_id", str)
    @Out("success_code", int)
    def delete_flavor(self, flavor_id):
        """
        Deletes a flavor from the database and OpenStack.

        :param flavor_id: The id of the flavor.
        :return: 200, if successful. 404, if not found.
        """

        flavor_id = str(flavor_id)

        self.logger.info("Delete flavor with id " + str(flavor_id) + "...")

        session = self.db.get_session()

        flavor = session.query(Flavor).filter(Flavor.flavor_id == flavor_id).first()
        if flavor is None:
            self.logger.warning("No flavor found with id " + str(flavor_id) + " in MaSta database.")
            return 404
        else:
            self.masta_agents[int(flavor.datacenter_id)].delete_flavor(flavor.flavor_os_id)

            session.delete(flavor)

            session.commit()

            self.logger.info("Deleted flavor with id " + str(flavor_id) + ".")

            return 200

    # ----------------------------------------------------------
    # IMAGES
    # ----------------------------------------------------------

    @In("image_data", dict)
    @Out("success_code", int)
    def create_image(self, image_data):
        """
        Stores an image in OpenStack.

        :param image_data:  A ImageData object containing data about the image.
        :return: 201: image created. 200: image already exists, not created
        """

        self.logger.info("Create new image...")

        session = self.db.get_session()

        image_data = image_data["image"]

        # Check, if image exists already
        if session.query(Image).filter(Image.image_id == image_data["image_id"].replace('-', '')).first() is not None:
            self.logger.warning("An image with id " + image_data["image_id"] + " already exists in the MaSta database.")
            return 200
        else:

            # Download image file into temporary folder

            self.logger.info("Download image into temporary folder...")

            tmp_image_dir = TMPDIR + str(time.time()) + "-" + image_data["url"].split("/")[-1]
            imagefile = urllib.URLopener()
            imagefile.retrieve(image_data["url"], tmp_image_dir)

            self.logger.info("Download finished.")

            # Tell masta agent to store image

            self.logger.info("Upload image to OpenStack...")

            if "container_format" in image_data:
                container_format = image_data["container_format"]
            else:
                container_format = "bare"

            if "disk_format" in image_data:
                disk_format = image_data["disk_format"]
            else:
                disk_format = "qcow2"

            os_image_data = {
                "name": image_data["name"],
                "container_format": container_format,
                "disk_format": disk_format
            }

            os_image_id = self.masta_agents[int(image_data["datacenter_id"])].create_image(os_image_data, tmp_image_dir)

            self.logger.info("Upload finished.")

            # Insert image into database

            image = Image(image_id=image_data["image_id"],
                          datacenter_id=image_data["datacenter_id"],
                          image_os_id=os_image_id,
                          description=image_data["description"])

            session.add(image)

            session.commit()
            self.logger.info("Created new image with id " + str(image.image_id) + ".")

            return 201

    @In("image_id", str)
    @Out("success_code", int)
    def delete_image(self, image_id):
        """
        Deletes an image from the database and OpenStack.

        :param image_id: The id of the image.
        :return: 200, if successful. 404, if not found.
        """

        image_id = str(image_id)

        self.logger.info("Delete image with id " + str(image_id) + "...")

        session = self.db.get_session()

        image = session.query(Image).filter(Image.image_id == image_id).first()
        if image is None:
            self.logger.warning("No image found with id " + str(image_id) + " in MaSta database.")
            return 404
        else:
            self.masta_agents[image.datacenter_id].delete_image(image.image_os_id)

            session.delete(image)

            session.commit()

            self.logger.info("Deleted image with id " + str(image_id) + "...")

            return 200

    # ----------------------------------------------------------
    # NETWORKS
    # ----------------------------------------------------------

    @In("vm_instance_id", str)
    @Out("instance_ip", str)
    def get_vm_mgmt_ip(self, vm_instance_id, session=None):
        """
        Retrieves the management IP address of an instance.

        :param vm_instance_id: The id of the VM instance.
        :return: The ip of the instance.
        """

        if session is None:
            session = self.db.get_session()

        vm_instance = session.query(VMInstance).filter(VMInstance.vm_instance_id == vm_instance_id).first()
        if vm_instance is None:
            self.logger.warning("No VM instance found with id " + str(vm_instance_id) + " in MaSta database.")
            return 404
        else:
            management_network = session.query(ManagementNetwork).filter(ManagementNetwork.datacenter_id == vm_instance.datacenter_id).first()
            if management_network is None:
                self.logger.warning("No management network found in datacenter " + str(vm_instance.datacenter_id) + ".")
                return 404
            instance_ip = self.masta_agents[vm_instance.datacenter_id].get_vm_ip(vm_instance.vm_os_id, management_network.network_os_name)
            return instance_ip

    # ----------------------------------------------------------
    # MONITORING DATA
    # ----------------------------------------------------------

    @In("monitoring_request", dict)
    @Out("monitoring_response", dict)
    def get_monitoring_data(self, monitoring_request):
        """
        Retrieves monitoring data for a specific VM.

        :param monitoring_request: A MonitoringRequest object.
        :return: A MonitoringResponse object.
        """

        monitoring_request = monitoring_request["monitoring_request"]

        session = self.db.get_session()

        # First, get the VM instance

        vm_instance = session.query(VMInstance).filter(VMInstance.vm_instance_id == monitoring_request["vm_instance_id"]).first()
        if vm_instance is None:
            raise Exception("There is no VM instance with id " + monitoring_request["vm_instance_id"] + ".")

        # Second, call the methods on Ceilometer to obtain the values

        if monitoring_request["type"] == "memory_usage":
            current = self.masta_agents[vm_instance.datacenter_id].get_monitoring_value(vm_instance.vm_os_id, "memory.usage")
            total = self.masta_agents[vm_instance.datacenter_id].get_monitoring_value(vm_instance.vm_os_id, "memory")

        elif monitoring_request["type"] == "cpu_util":
            current = self.masta_agents[vm_instance.datacenter_id].get_monitoring_value(vm_instance.vm_os_id, "cpu_util")
            total = 1

        #elif monitoring_request["type"] == "disk_usage":
        #    current = self.masta_agents[vnf.datacenter_id].get_monitoring_value(vnf.vm_os_id, "disk.allocation")
        #    total = self.masta_agents[vnf.datacenter_id].get_monitoring_value(vnf.vm_os_id, "disk.capacity")
        else:
            raise Exception("There is no type " + monitoring_request["type"] + " supported.")

        monitoring_response = {
            "monitoring_response" : {
                "type" : monitoring_request["type"],
                "vm_instance_id" : monitoring_request["vm_instance_id"],
                "value" : {
                    "current": current,
                    "total": total
                }
            }
        }

        return monitoring_response

    @In("monitoring_alarm_request", dict)
    @Out("subscription_name", str)
    def create_monitoring_alarm(self, monitoring_alarm_request):
        """
        Sets up an alarm and returns a subscription id to subscribe to the message broker.

        :param monitoring_alarm_request: A MonitoringAlarmRequest object containing data about the alarm to be set up.
        :return: The name of the subscription
        """

        self.logger.info("Create new monitoring alarm...")

        session = self.db.get_session()
        session.commit()

        monitoring_alarm_request = monitoring_alarm_request["monitoring_alarm_request"]

        # Retrieve matching data
        vm_instance = session.query(VMInstance).filter(VMInstance.vm_instance_id == monitoring_alarm_request["vm_instance_id"]).first()
        if vm_instance is None:
            self.logger.error("There is no VM instance with id " + str(monitoring_alarm_request["vm_instance_id"]) + ".")
            return 500

        # Put alarm in database (need the unique id for a unique name)
        monitoring_alarm = MonitoringAlarm(
                datacenter_id=vm_instance.datacenter_id,
                alarm_os_id="not-set",
                type=monitoring_alarm_request["type"],
                vm_instance_id=monitoring_alarm_request["vm_instance_id"],
                comparison_operator=monitoring_alarm_request["comparison_operator"],
                threshold=monitoring_alarm_request["threshold"],
                threshold_type=monitoring_alarm_request["threshold_type"],
                statistic=monitoring_alarm_request["statistic"],
                period=monitoring_alarm_request["period"]
        )
        session.add(monitoring_alarm)
        session.flush()

        # Set up the alarm in OpenStack
        monitoring_alarm_request["vm_os_id"] = vm_instance.vm_os_id
        monitoring_alarm_request["mastaserver_url"] = self.mastaserver_url
        monitoring_alarm_request["name"] = "Alarm-" + str(monitoring_alarm.monitoring_alarm_id)

        # Choose meter names
        if monitoring_alarm_request["type"] == "memory_usage":
            meter = "memory.usage"
            if monitoring_alarm_request["threshold_type"] == "relative": # transform threshold to absolute value
                total_value = self.get_monitoring_data({
                    "monitoring_request": {
                        "type": "memory_usage",
                        "vm_instance_id": vm_instance.vm_instance_id
                    }
                })["monitoring_response"]["value"]["total"]
                monitoring_alarm_request["threshold"] = total_value * monitoring_alarm_request["threshold"]
        elif monitoring_alarm_request["type"] == "cpu_util":
            meter = "cpu_util"
        #elif monitoring_alarm_request["type"] == "disk_usage":
        #    meter = "disk.usage"

        monitoring_alarm_request["type"] = meter

        alarm_os_id = self.masta_agents[vm_instance.datacenter_id].create_monitoring_alarm(monitoring_alarm_request)

        # Update the database
        monitoring_alarm.alarm_os_id = alarm_os_id
        session.commit()

        # Return subscription
        subscription_name = "masta.alarm." + str(vm_instance.vm_instance_id) + "." + str(monitoring_alarm.monitoring_alarm_id)

        self.logger.info("Created new monitoring alarm published under " + str(subscription_name) + ".")

        return subscription_name

    @In("subscription_name", str)
    @Out("success_code", int)
    def delete_monitoring_alarm(self, subscription_name):
        """
        Delete monitoring alarm by subscription_name.

        :param subscription_name: The name of the Subscription.
        :return: 200, if successful. 404, if not found.
        """

        subscription_name = str(subscription_name)

        self.logger.info("Delete monitoring alarm under subscription name " + str(subscription_name) + "...")

        monitoring_alarm_id = int(subscription_name.split(".")[3])

        return self.delete_monitoring_alarm_by_id(monitoring_alarm_id)

    @In("monitoring_alarm_id", int)
    @Out("success_code", int)
    def delete_monitoring_alarm_by_id(self, monitoring_alarm_id):
        """
        Delete monitoring alarm by alarm id.

        :param monitoring_alarm_id: The id of the alarm, under which it is registered in the MaSta database.
        :return: 200, if successful. 404, if not found.
        """

        session = self.db.get_session()

        self.logger.info("Delete monitoring alarm under alarm id " + str(monitoring_alarm_id) + "...")

        monitoring_alarm_id = int(monitoring_alarm_id)
        monitoring_alarm = session.query(MonitoringAlarm).filter(MonitoringAlarm.monitoring_alarm_id == monitoring_alarm_id).first()

        if monitoring_alarm is None:
            self.logger.warning("No monitoring alarm found with alarm id " + str(monitoring_alarm_id) + " in MaSta database.")
            return 404
        else:
            # Delete from OpenStack

            self.masta_agents[monitoring_alarm.datacenter_id].delete_monitoring_alarm(monitoring_alarm.alarm_os_id)

            # Delete from the database

            session.delete(monitoring_alarm)
            session.commit()

            self.logger.info("Deleted monitoring alarm under alarm id " + str(monitoring_alarm_id) + ".")

            return 200

    @Out("success_code", int)
    def delete_all_monitoring_alarms(self):
        """
        Deletes all monitoring alarms in the DB.

        :return: 200, if successful.
        """

        self.logger.info("Delete all monitoring alarms...")

        session = self.db.get_session()
        session.commit()

        for monitoring_alarm in session.query(MonitoringAlarm).all():
            self.delete_monitoring_alarm_by_id(monitoring_alarm.monitoring_alarm_id)

        self.logger.info("Deleted all monitoring alarms.")

        return 200

    def invoke_monitoring_alarm(self, data):
        """
        Internal method. Called by the MaSta-Server when an alarm message arrives.

        :param data: data
        :return:
        """

        self.logger.info("Received a monitoring alarm...")

        session = self.db.get_session()
        session.commit()

        # Parse the data
        self.logger.debug(json.dumps(data, indent=4))
        alarm_os_id = data["alarm_id"]

        monitoring_alarm = session.query(MonitoringAlarm).filter(MonitoringAlarm.alarm_os_id == alarm_os_id).first()
        if monitoring_alarm is None:
            self.logger.error("Could not find any alarm registered under OS id " + str(alarm_os_id) + ".")

        subscription_name = "masta.alarm." + str(monitoring_alarm.vm_instance_id) + "." + str(monitoring_alarm.monitoring_alarm_id)

        monitoring_alarm_event = {
            "monitoring_alarm_event": {
                "subscription_name": subscription_name,
                "value": data["reason_data"]["most_recent"],
                "monitoring_alarm_request": {
                    "type": monitoring_alarm.type,
                    "vm_instance_id": str(monitoring_alarm.vm_instance_id),
                    "comparison_operator": monitoring_alarm.comparison_operator,
                    "threshold": monitoring_alarm.threshold,
                    "threshold_type": monitoring_alarm.threshold_type,
                    "statistic": monitoring_alarm.statistic,
                    "period": monitoring_alarm.period
                }
            }
        }

        self.logger.debug(json.dumps(monitoring_alarm_event, indent=4))

        # Publish
        self.rpc.publish(subscription_name, monitoring_alarm_event)

        self.logger.info("Processed alarm and published under " + subscription_name + ".")


def daemon():
    daemonize(Masta)

if __name__ == '__main__':
    daemon()
