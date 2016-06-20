"""
sandman_pasta reimplements the behaviour of decaf-masta, but instead evaluates all calls to deployable heat templates
"""

import json

from decaf_storage.json_base import StorageJSONEncoder
from decaf_storage import Endpoint

from decaf_utils_components.base_daemon import daemonize
import yaml
import time
import urllib
from decaf_utils_components import BasePlugin, In, Out
import base64
import sys
import math
import traceback

__author__ = "Banana PG-SANDMAN"
__date__ = "$01-jun-2016$"

TMPDIR = "/tmp/decaf/"


class Pasta(BasePlugin):
    __version__ = "0.1-dev01"
    datacenters = dict()
    config = None
    logger = None

    def __init__(self, logger=None, config=None):
        super(Pasta, self).__init__(logger=logger, config=config)
        with open('/etc/decaf/pastad.cfg') as file:
            self.config = yaml.safe_load(file)

        if self.config is None:
            self.logger.error("No configuration file found or not in yaml format.")
            sys.exit(1)

        try:
            self.datacenters = self.config["datacenters"]
        except KeyError as e:
            self.logger.error("Please check the configuration. There is no datacenter defined.")
            sys.exit(1)
        self.logger.debug('Configuration seems sane.')

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    # same behaviour as masta
    def _after_connect(self):
        self.rpc.set_json_encoder(StorageJSONEncoder)
        self.storage = Endpoint(self.rpc, self.logger)

        # Check if all the datacenters are also registered in Storage, if not, register them

        storage_datacenters = self.storage.get('datacenter', options=[], filters={})


    def connect(self, url=None, rpc=None, routing_key=None):
        # fake being masta, so we don't have to change other code
        super(Pasta, self).connect(self.config["rpc"]["url"], None, "decaf_masta")

    @In("datacenter_id", int)
    @Out("success_code", int)
    def initialize_datacenter(self, datacenter_config):
        """
        Reimplemented method of decaf_masta

        :param datacenter_config: A DatacenterConfig object describing the datacenter to be added.
        :return: The id of the new entry.
        """
        self.logger.info("Call to initialize_datacenter")
        return 0

    @In("keystone_credentials", dict)
    @Out("keystone_id", int)
    def create_keystone_credentials(self, keystone_credentials):
        self.logger.info("Call to create_keystone_credentials")
        return 0


    @In("keystone_id", int)
    @Out("keystone_credentials", dict)
    def get_keystone_credentials(self, keystone_id):
        """
        Gets a keystone entry from the database.

        :param keystone_id: The id of the database entry.
        :return: The data of the keystone entry with the given id, or an error code if not found.
        """

        return 400


    @Out("keystone_list", list)
    def get_keystones(self):
        """
        Get keystone entries contained in the database.

        :return: A list of keystone entries currently existing in the Masta database.
        """

        return None


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

        return int(datacenter.datacenter_id)


    @Out("datacenter_list", list)
    def get_datacenters(self):
        """
        Get datacenter entries contained in the database.

        :return: A list of datacenter entries currently existing in the Masta database.
        """

        return [datacenter.to_dict() for datacenter in self.datacenters]


    @In("datacenter_id", int)
    @Out("datacenter_stats", dict)
    def get_datacenter_stats(self, datacenter_id):
        """
        Returns information about the datacenter.

        :param datacenter_id: The id of the datacenter.
        :return: A list of datacenter entries currently existing in the Masta database
        """

        return datacenter_stats


    @In("datacenter_id", int)
    @Out("ip_namespace", str)
    def get_datacenter_ip_namespace(self, datacenter_id):
        """
        Returns the name of the IP namespace of the router on the given datacenter.

        :param datacenter_id: The masta id of the datacenter.
        :return: IP namespace name.
        """

        ip_namespace = "qrouter-1"

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

        return 200


    @Out("success_code", int)
    def destroy_all_scenarios(self):
        """
        Destroys all scenarios in the MaSta database.

        :return: 200, if successful.
        """

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

        return 200


    @In("shrink_graph", dict)
    @Out("success_code", int)
    def shrink_scenario(self, shrink_graph):
        """
        Method to shrink an existing scenario.

        :param shrink_graph: An object of type InstanceGraph that lists all the nodes and edges to delete.
        :return: 200, if successful.
        """

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

        pass


    def create_edges(self, instance_graph, session):
        """
        Internal method to create edges in the database and set up the networks in OpenStack.

        :param instance_graph: The graph of the scenario.
        :param session: The session object.
        :return:
        """
        pass


    def rollback(self, instance_graph, session, del_scenario=False):
        """
        Internal method to rollback the creation or altering of a scenario.

        :param instance_graph: The graph of the scenario.
        :param session: The session object.
        :return:
        """
        pass


    def delete_nodes(self, vm_instance_id_list, session):
        """
        Internal method to delete nodes from a scenario.

        :param scenario_instance_id: The id of the scenario.
        :param session: The session object.
        :return: 200, if successful.
        """

        return 200


    def delete_edges(self, edge_list, session):
        """
        Internal method to delete edges from a scenario.

        :param edge_list: A list containing objects of internal edges, management ports and public ports from the db.
        :param session: The session object.
        :return:
        """

        pass


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

        return 200


    @In("scenario_action", dict)
    @Out("success_code", int)
    def action_scenario(self, scenario_action):
        """
        Perform an action on a scenario.

        :param scenario_action: A dictionary of type ScenarioAction containing the scenario instance id and the action to perform.
        :return: 200, if successful.
        """

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

        return 201


    @In("flavor_id", str)
    @Out("success_code", int)
    def delete_flavor(self, flavor_id):
        """
        Deletes a flavor from the database and OpenStack.

        :param flavor_id: The id of the flavor.
        :return: 200, if successful. 404, if not found.
        """

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

        return 201


    @In("image_id", str)
    @Out("success_code", int)
    def delete_image(self, image_id):
        """
        Deletes an image from the database and OpenStack.

        :param image_id: The id of the image.
        :return: 200, if successful. 404, if not found.
        """

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

        return "10.0.0.1"


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

        monitoring_response = {
            "monitoring_response": {
                "type": monitoring_request["type"],
                "vm_instance_id": monitoring_request["vm_instance_id"],
                "value": {
                    "current": 10,
                    "total": 100
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

        return "test"


    @In("subscription_name", str)
    @Out("success_code", int)
    def delete_monitoring_alarm(self, subscription_name):
        """
        Delete monitoring alarm by subscription_name.

        :param subscription_name: The name of the Subscription.
        :return: 200, if successful. 404, if not found.
        """


        return 200


    @In("monitoring_alarm_id", int)
    @Out("success_code", int)
    def delete_monitoring_alarm_by_id(self, monitoring_alarm_id):
        """
        Delete monitoring alarm by alarm id.

        :param monitoring_alarm_id: The id of the alarm, under which it is registered in the MaSta database.
        :return: 200, if successful. 404, if not found.
        """

        return 200


    @Out("success_code", int)
    def delete_all_monitoring_alarms(self):
        """
        Deletes all monitoring alarms in the DB.

        :return: 200, if successful.
        """

        return 200


    def invoke_monitoring_alarm(self, data):
        """
        Internal method. Called by the MaSta-Server when an alarm message arrives.

        :param data: data
        :return:
        """

        pass


def daemon():
    daemonize(Pasta)


if __name__ == '__main__':
    daemon()
