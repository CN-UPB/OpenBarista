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
decaf-masta implements all the methods to interact with OpenStack and OpenDaylight.
"""

import json

import requests


class MastaAgent():
    def __init__(self, logger, datacenter_id, datacenter_name, keystone_region, keystone_url, keystone_domain_id, keystone_domain_name, keystone_project_name,  keystone_user, keystone_pass):
        self.logger = logger
        self.datacenter_id = datacenter_id
        self.datacenter_name = datacenter_name
        self.keystone_region = keystone_region
        self.keystone_url = keystone_url
        self.keystone_domain_id = keystone_domain_id
        self.keystone_domain_name = keystone_domain_name
        self.keystone_project_name = keystone_project_name
        self.keystone_user = keystone_user
        self.keystone_pass = keystone_pass

    # Methods for authentification

    def get_openstack_token(self):
        """
        Retrieves an OpenStack token to access its services.

        :return: The token object
        """

        headers_req = {"Content-Type": "application/json", "User-Agent": "python-decaf-masta"}

        #curl -i -X POST http://controller:35357/v3/auth/tokens -H "Content-Type: application/json" -H "User-Agent: python-decaf-masta" -d '{"auth": {"identity": {"methods": ["password"], "password": { "user": {"domain": {"id": "default", "name": "Default"}, "name": "admin", "password": "1JIGMx1SP82uCg"}}}}}'

        auth =  {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "id": self.keystone_domain_id,
                                "name": self.keystone_domain_name
                            },
                            "name": self.keystone_user,
                            "password": self.keystone_pass
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": self.keystone_project_name,
                        "domain": {
                            "id": self.keystone_domain_id,
                            "name": self.keystone_domain_name
                        }
                    }
                }
            }
        }

        response = requests.post(self.keystone_url + "/auth/tokens", headers = headers_req, data=json.dumps(auth))

        #self.logger.debug(response.text)

        if response.status_code == 201:
            return {"token":
                {
                    "id": response.headers["X-Subject-Token"],
                    "catalog": json.loads(response.text)["token"]["catalog"],
                    "user_id": json.loads(response.text)["token"]["user"]["id"],
                    "project_id": json.loads(response.text)["token"]["project"]["id"]
                }
            }

        else:
            raise BaseException(response.text)

    def get_headers(self, token):
        """
        Creates the headers element.

        :param token: The token object.
        :return: The headers object.
        """

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "python-decaf-masta",
            "Accept": "application/json",
            "X-Auth-Token": token["token"]["id"]
        }

        #self.logger.debug(headers)

        return headers

    def get_service_url(self, token, service_name):
        """
        Retrieves the URL of a service.

        :param token: The token object.
        :param service_name: The name of the service.
        :return: The Url of the service.
        """

        for service in token["token"]["catalog"]:
            if service["type"] == service_name:
                for endpoint in service["endpoints"]:
                    if endpoint["region_id"] == self.keystone_region and endpoint["interface"] == "public":
                        return endpoint["url"]
                raise BaseException("There is no endpoint for service " + service_name + " in region " + self.keystone_region + ".")
        raise BaseException("There is no " + service_name + " service registered.")

    # VM-INSTANCES

    def new_vm_instance(self, instance_data):
        """
        Creates a new VM instance in OpenStack. Returns the OpenStack-ID.

        :param instance_data: A dictionary containing information about the VM.
        :return:
        """
        
        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        response = requests.post(self.get_service_url(token, "compute")+"/servers", headers=headers_req, data=json.dumps(instance_data))

        if response.status_code == 202:
            response_data = json.loads(response.text)
            return response_data
        else:
            raise BaseException(response.text)

    def delete_vm_instance(self, instance_id):
        """
        Deletes a VM instance from OpenStack.

        :param instance_id: The OpenStack ID of the instance.
        :return: True, if successful.
        """
        
        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        response = requests.delete(self.get_service_url(token, "compute")+"/servers/"+instance_id, headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no VM with id " + str(instance_id) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    def action_vm_instance(self, instance_id, instance_action):
        """
        Performs an action on the VM with the given id.

        :param instance_id: The OpenStack ID of the instance.
        :param instance_action: The action to be performed.
        :return:
        """

        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        payload_req = {}

        if instance_action == "start":
            payload_req["os-start"] = None
        elif instance_action == "stop":
            payload_req["os-stop"] = None
        elif instance_action == "soft-reboot":
            payload_req["reboot"] = {
                "type": "SOFT"
            }
        elif instance_action == "hard-reboot":
            payload_req["reboot"] = {
                "type": "HARD"
            }
        elif instance_action == "pause":
            payload_req["pause"] = None
        elif instance_action == "unpause":
            payload_req["unpause"] = None
        elif instance_action == "suspend":
            payload_req["suspend"] = None
        elif instance_action == "resume":
            payload_req["resume"] = None
        elif instance_action == "shelve":
            payload_req["shelve"] = None
        elif instance_action == "unshelve":
            payload_req["unshelve"] = None
        else:
            raise BaseException("The specified action is not supported.")

        response = requests.post(self.get_service_url(token, "compute") + "/servers/" + instance_id + "/action", headers = headers_req, data=json.dumps(payload_req))

        if response.status_code == 202:
            return True
        else:
            raise BaseException(response.text)

    # KEYS

    def create_keypair(self, keypair_name):
        """
        Creates a new key to provide ssh access.

        :param keypair_name: The name of the keypair
        :return: The dictionary that OpenStack returns.
        """

        keypair = {
            "keypair": {
                "name": keypair_name
            }
        }

        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        response = requests.post(self.get_service_url(token,"compute") + "/os-keypairs",
                                 headers=headers_req,
                                 data=json.dumps(keypair))

        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data
        else:
            raise BaseException(response.text)

    def delete_keypair(self, keypair_name):
        """
        Deletes a keypair.

        :param keypair_name: String
        :return: True, if successful.
        """

        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        response = requests.delete(self.get_service_url(token, "compute")+"/os-keypairs/"+keypair_name, headers=headers_req)

        if response.status_code == 202:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no keypair with name " + str(keypair_name) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    # FLAVORS

    def create_flavor(self, flavor_data):
        """
        Creates a new flavor.

        :param flavor_data: A dictionary containing flavor data.
        :return: The id of the flavor.
        """

        flavor = {
            "flavor": {
                "name": flavor_data["flavor_id"] + "-" + flavor_data["name"],
                "ram": flavor_data["ram"],
                "vcpus": flavor_data["vcpus"],
                "disk": flavor_data["disk"]
            }
        }

        token = self.get_openstack_token()

        headers_req = self.get_headers(token)
        
        response = requests.post(self.get_service_url(token, "compute")+"/flavors", headers = headers_req, data=json.dumps(flavor))

        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data["flavor"]["id"]
        else:
            raise BaseException(response.text)

    def delete_flavor(self, flavor_id):
        """
        Deletes a flavor.

        :param flavor_id: The if of the flavor.
        :return: True, if successful
        """
        
        token = self.get_openstack_token()

        headers_req = self.get_headers(token)
        
        response = requests.delete(self.get_service_url(token, "compute")+"/flavors/"+flavor_id, headers = headers_req)

        if response.status_code == 202:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no flavor with id " + str(flavor_id) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    # IMAGES

    def create_image(self, image_data, image_path):
        """
        Creates a new image and uploads it into OpenStack.

        :param image_data: Object containing information about the image.
        :param image_path: The url of the image.
        :return: The id of the image.
        """
        
        token = self.get_openstack_token()
        glance_url = self.get_service_url(token, "image")

        # first, create an image in the database (without the binaries yet)

        headers_req = self.get_headers(token)

        response = requests.post(glance_url + "/v2/images", headers = headers_req, data=json.dumps(image_data))

        if response.status_code != 201:
            raise BaseException(response.text)

        # image correctly set up, now extract id

        response_data = json.loads(response.text)
        image_id = response_data["id"]

        # now upload the binaries from the given location

        data = open(image_path, 'rb')

        headers_req["Content-Type"] = "application/octet-stream"

        response = requests.put(glance_url + "/v2/images/" + image_id + "/file", headers = headers_req, data = data)
        
        if response.status_code == 204:
            return image_id
        else:
            raise BaseException(response.text)

    def delete_image(self, image_id):
        """
        Deletes an image from OpenStack.

        :param image_id: The id of the image.
        :return: True, if successful.
        """
        
        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        response = requests.delete(self.get_service_url(token, "image")+"/v2/images/"+image_id, headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no image with id " + str(image_id) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    # NETWORKING

    def get_vm_ip(self, vm_os_id, network_name):
        """
        Gets the ip of the vm for a given network.

        :param vm_os_id: The id of the VM instance.
        :param network_name: The name of the network.
        :return: The IP address of the VM.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.get(self.get_service_url(token, "compute")+"/servers/"+vm_os_id, headers = headers_req)
        response_data=json.loads(response.text)

        if response.status_code == 200:
            self.logger.debug(response_data)
            ip_list = response_data["server"]["addresses"]
            if network_name not in ip_list:
                self.logger.warning("The given VM does not have IPs in network " + network_name + ".")
                return "0.0.0.0"

            ip_list_network = ip_list[network_name]

            for ip_dict in ip_list_network:
                if ip_dict["OS-EXT-IPS:type"] == "fixed":
                    return ip_dict["addr"]

            self.logger.warning("The given VM does not have a fixed IP address.")
            return "0.0.0.0"
        else:
            raise BaseException(response.text)

    def get_net_list(self):
        """
        Get the list of available networks.
        """
        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.get(self.get_service_url(token,"network")+"/v2/networks",headers = headers_req)
        if response.status_code != 200:
            raise BaseException(response.text)

        response_data=json.loads(response.text)
        return response_data
        
    def get_subnet_list(self):
        """
        Get the list of available networks.
        """
        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.get(self.get_service_url(token,"network")+"/v2/subnets",headers = headers_req)
        if response.status_code != 200:
            raise BaseException(response.text)

        response_data=json.loads(response.text)
        return response_data

    def attach_vm_to_net(self, vm_os_id, port_os_id):
        """
        Attaches VM to a network.

        :param os_port_id: The id of the port.
        :return: The result of the OpenStack call.
        """

        token = self.get_openstack_token()

        headers_req = self.get_headers(token)

        payload_req = {
            "interfaceAttachment": {
                "port_id": port_os_id
            }
        }

        response = requests.post(self.get_service_url(token, "compute")+"/servers/" + vm_os_id + "/os-interface",
                                 headers=headers_req,
                                 data=json.dumps(payload_req))

        if response.status_code == 200:
            response_data = json.loads(response.text)
            return response_data
        elif response.status_code == 409:
            # Instance is still spawning...
            return 409
        else:
            self.logger.debug(str(response.status_code))
            raise BaseException(response.text)

    def list_ports(self, net_id):
        """
        Lists all the ports of a net.

        :param net_id: The id of the network.
        :return: The result of the OpenStack call.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.get(self.get_service_url(token, "network")+"/v2.0/ports?network_id="+net_id, headers=headers_req)

        if response.status_code != 200:
            raise BaseException(response.text)

        response_data = json.loads(response.text)

        return response_data

    def create_port(self, net_id):
        """
        Creates a new port.

        :param net_id: The id of the network.
        :return: The result of the OpenStack call.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        payload_req = {
            "port": {
                "network_id": net_id,
                "admin_state_up": True
            }
        }

        response = requests.post(self.get_service_url(token, "network")+"/v2.0/ports",
                                 headers=headers_req,
                                 data=json.dumps(payload_req))

        if response.status_code != 201:
            raise BaseException(response.text)

        response_data = json.loads(response.text)
        return response_data

    def delete_port(self, port_id):
        """
        Deletes a port from OpenStack.

        :param port_id: The id of the port.
        :return: True, if successful.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)
        response = requests.delete(self.get_service_url(token, "network")+"/v2.0/ports/"+port_id, headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no port with id " + str(port_id) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    def add_router_interface(self, subnet_id, router_id):
        """
        Attaches a subnet to a router.

        :param subnet_id: The id of the subnet.
        :param router_id: The id of the router to attach the subnet to.
        :return: True, if successful.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        payload_req = {
            "subnet_id": subnet_id
        }

        self.logger.debug(self.get_service_url(token, "network"))
        response = requests.put(self.get_service_url(token, "network") + "/v2.0/routers/" + router_id + "/add_router_interface",
                                 headers=headers_req,
                                 data=json.dumps(payload_req))

        if response.status_code == 200:
            return True
        else:
            raise BaseException(response.text)

    def update_router(self, router_id, router_data):
        """
        Updates the router.

        :param router_id: The id of the router.
        :param router_data: Data object to update.
        :return: True, if successful.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.put(self.get_service_url(token, "network") + "/v2.0/routers/" + router_id,
                                 headers=headers_req,
                                 data=json.dumps(router_data))

        if response.status_code == 200:
            return True
        else:
            raise BaseException(response.text)



    def create_floating_ip(self, external_net_id, port_id):
        """
        Creates a new floating ip.

        :param external_net_id: The id of the external network for the floating ip.
        :param port_id: The id of the port to associate the floating ip to.
        :return: True, if successful.
        """
        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        payload_req = {
            "floatingip": {
                "floating_network_id": external_net_id,
                "port_id": port_id
            }
        }

        response = requests.post(self.get_service_url(token, "network")+"/v2.0/floatingips",
                                 headers=headers_req,
                                 data=json.dumps(payload_req))

        if response.status_code != 201:
            raise BaseException(response.text)

        response_data = json.loads(response.text)
        return response_data

    def delete_floating_ip(self, floating_ip_id):
        """
        Deletes a floating IP from OpenStack.

        :param floating_ip_id: Id of the floating IP.
        :return: True, if successful.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.delete(self.get_service_url(token, "network")+"/v2.0/floatingips/"+floating_ip_id, headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no floating ip with id " + str(floating_ip_id) + " to delete in datacenter " + str(self.datacenter_id) + ".")
            return True
        else:
            raise BaseException(response.text)

    def create_net(self, net_data):
        """
        Creates a network in OpenStack.

        :param net_data: Data specifying the network.
        :return: The id of the network.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)
        
        response = requests.post(self.get_service_url(token, "network")+"/v2.0/networks",headers = headers_req,data = json.dumps(net_data))

        if response.status_code != 201:
            raise BaseException(response.text)
        else:
            response_data=json.loads(response.text)
            return response_data["network"]["id"]

    def delete_net(self, net_id):
        """
        Deletes a network from OpenStack.

        :param net_id: The id of the network.
        :return: True, if successful.
        """

        token=self.get_openstack_token()
        headers_req = self.get_headers(token)
        response = requests.delete(self.get_service_url(token, "network")+"/v2.0/networks/"+net_id,headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no network with id "+str(net_id)+" to delete in datacenter "+str(self.datacenter_id))
            return True
        else:
            raise BaseException(response.text)

    def create_subnet(self, subnet_data):
        """
        :param subnet_data: Data specifying the subnet.
        :return: The subnet id.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.post(self.get_service_url(token, "network")+"/v2.0/subnets",headers = headers_req,data = json.dumps(subnet_data))
        if response.status_code == 201:
            response_data=json.loads(response.text)
            return response_data["subnet"]["id"]
        else:
            raise BaseException(response.text)

    def delete_subnet(self, subnet_id):
        """
        Deletes a subnetwork from OpenStack.

        :param subnet_id: The id of the subnet to delete.
        :return: True, if successful.
        """

        token=self.get_openstack_token()
        headers_req = self.get_headers(token)
        response = requests.delete(self.get_service_url(token,"network")+"/v2.0/subnets/"+subnet_id, headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no subnet with id "+str(subnet_id)+" to delete in datacenter "+str(self.datacenter_id))
            return True
        else:
            raise BaseException(response.text)

    def create_router(self, router_data):
        """
        Creates a router in OpenStack.

        :param router_data: Data specifying the router.
        :return: The router id.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.post(self.get_service_url(token, "network")+"/v2.0/routers",headers = headers_req,data = json.dumps(router_data))
        if response.status_code == 201:
            response_data=json.loads(response.text)
            return response_data["router"]["id"]
        else:
            raise BaseException(response.text)

    # MONITORING DATA

    def get_monitoring_value(self,vm_os_id,meter_name):
        """
        Retrieves a monitoring value from OpenStack.

        :param vm_os_id: The id of the VM to retrieve information from.
        :return: The value.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        filter = "?q.field=resource_id&q.op=eq&q.type=&q.value="+vm_os_id

        response = requests.get(self.get_service_url(token,"metering")+"/v2/meters/"+meter_name+filter, headers = headers_req)

        if response.status_code == 200:
            if len(json.loads(response.text)) == 0:
                raise BaseException("There are no samples for virtual machine with OS id " + vm_os_id + " and meter name " + meter_name)
            return json.loads(response.text)[0]["counter_volume"]
        else:
            raise BaseException(response.text)

    def create_monitoring_alarm(self,monitoring_alarm_request):
        """
        Creates an alarm.

        :param monitoring_alarm_request: Dictionary that contains the data of the alarm.
        :return: The id of the alarm.
        """

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        payload_req = {
            "alarm_actions": [
                "http://"+monitoring_alarm_request["mastaserver_url"] + "/alarm"
            ],
            "alarm_id": None,
            "threshold_rule": {
                "comparison_operator": monitoring_alarm_request["comparison_operator"],
                "evaluation_periods": 1,
                "exclude_outliers": False,
                "meter_name": monitoring_alarm_request["type"],
                "period": monitoring_alarm_request["period"],
                "query": [
                    {
                        "field": "resource_id",
                        "op": "eq",
                        "type": "string",
                        "value": monitoring_alarm_request["vm_os_id"]
                    }
                ],
                "statistic": monitoring_alarm_request["statistic"],
                "threshold": monitoring_alarm_request["threshold"]
            },
            "enabled": True,
            "name": monitoring_alarm_request["name"],
            "project_id": str(token["token"]["project_id"]),
            "repeat_actions": False,
            "severity": "moderate",
            "state": "ok",
            "type": "threshold",
            "user_id": str(token["token"]["user_id"])
        }

        response = requests.post(self.get_service_url(token, "metering")+"/v2/alarms", headers = headers_req, data=json.dumps(payload_req))

        if response.status_code == 201:
            return json.loads(response.text)["alarm_id"]
        else:
            raise BaseException(response.text)
    
    def delete_monitoring_alarm(self,alarm_os_id):
        """
        Deletes an alarm.

        :param alarm_os_id: String
        :return:
        """
        
        token=self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.delete(self.get_service_url(token, "metering")+"/v2/alarms/"+alarm_os_id,headers = headers_req)

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            self.logger.warning("There is no alarm with id " + str(alarm_os_id) + " to delete in datacenter "+str(self.datacenter_id))
            return True
        else:
            raise BaseException(response.text)
    
    def get_datacenter_stats(self): # deprecated

        token = self.get_openstack_token()
        headers_req = self.get_headers(token)

        response = requests.get(self.get_service_url(token,"compute") + "/os-hypervisors/statistics", headers = headers_req)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise BaseException(response.text)