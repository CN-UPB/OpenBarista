##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

import traceback

from decaf_utils_components import BasePlugin
from decaf_vnf_manager_adapter.ssh_element_manager.ssh_element_manager import GenericSSHElementManager
from decaf_storage import Endpoint as Storage
from decaf_utils_components import In, Out

class VNF_Neighbor(object):

    def __init__(self, vnf_id):
        self.vnf_id = vnf_id
        self._links = dict()

    @property
    def links(self):
        return self._links

class Link(object):
    def __init__(self, vnfc_id,other_id, link_type):
        self.my_id = vnfc_id
        self.other_id = other_id
        self.link_type = link_type


class VNFC(object):
    """
    Model for a VNFC.
    """

    def __parse(self, desc):
        print desc
        id = desc["name"]

        if desc.get("auth",None):
            auth = desc["auth"]["username"],desc["auth"]["password"]
        else:
            auth = None
        files = desc.get("files",list())
        events = desc["events"]
        print id, auth, files, events
        return id, auth, files, events

    def __init__(self, vnfc_id=None, files=None, events=None, auth=None, desc=None):
        if desc is not None:
            vnfc_id, auth, files, events = self.__parse(desc)
            self._id = vnfc_id
            self._auth = auth
            self._files = files
            self._events = events
        else:
            self._id = vnfc_id
            self._auth = auth
            self._files = files
            self._events = events
        self.instances = list()

    @property
    def id(self):
        return self._id

    @property
    def files(self):
        return self._files

    @property
    def auth(self):
        return self._auth

    def set_auth(self, auth):
        self._auth = auth

    @property
    def events(self):
        return self._events




class GenericSSHVNFManager(BasePlugin):
    """
    Generates a VNF Manager from specification.
    """

    __version__ = "0.1-dev01"

    def __init__(self, vnf_instance_id = None, logger=None, *args, **kwargs):

        super(GenericSSHVNFManager, self).__init__(logger=logger, config=dict())
        self.vnf_instance_id = vnf_instance_id
        self.vnf_neighbors = dict()
        self._vnfcs = dict()

        # Root vnf id
        self.vnf_id =None

        # Element Descriptors
        self.instance_desc = None
        self.scenario_desc = None
        self.vnf_desc = None
        self.vnfc_descs = None

        self.vm_instances = dict()

        #Endpoints
        self.storage = None


    def _after_connect(self):

        self.storage = Storage(self.rpc, self.logger)

        try:
            self.instance_desc = self.storage.get("vnf_instance", options=[], filters={"uuid": self.vnf_instance_id})[0]
            self.scenario_desc = self.storage.get("scenario_instance", options=[], filters={"uuid": self.instance_desc["scenario_instance_id"]})
            self.vnf_desc = self.storage.get("vnf", options=[], filters={"uuid": self.instance_desc["vnf_id"]})
        except BaseException as e:
            self.logger.error("Error fetching required data : \n %s" % e)
            self.dispose()
            raise e
        else:
            self.update()

    @In("vm_instance_id", unicode)
    @Out("ack", bool)
    def new_vm_instance(self, vm_instance_id):
        """
        Creates an Element Manager for a VM instance.
        Can be called manually, but we suggest to use the update method instead.

        :param vnf_instance_id: The VNF instance id.
        :return: True, if successful. False otherwise.
        """

        def success(*args, **kwargs):
            self.logger.debug("Successfully connected")

        def fail(*args, **kwargs):
            self.logger.debug("Connection failed")

        if not self.vm_instances.get(vm_instance_id, None):
            try:
                self.logger.debug("Creating new Element-Manager for VM : %s" % vm_instance_id)
                mgr = GenericSSHElementManager(vm_instance_id=vm_instance_id, logger=self.logger, config=dict())
                mgr.connect(rpc=self.rpc, routing_key=vm_instance_id)
                mgr.connect_to_vm()
                self.vm_instances[vm_instance_id] = mgr
                return True
            except BaseException as e:
                traceback.print_exc()
                self.logger.error(e)
                self.logger.debug("Error while creating new Element-Manager for VM : %s" % vm_instance_id)
                raise e



    @Out("success", bool)
    def update(self):
        """
        Updates the Element Managers according to the VM instances registered in Storage.
        Deletes managers of instances that are not registered anymore, and creates ones that are registered, but not already created.

        :return: True, if successful. False otherwise.
        """

        self.logger.debug("Updating all Element-Managers")
        vm_instances = self.storage.get("vm_instance", options=[], filters={})
        self.logger.debug("Following VMs were found: \n %s" % vm_instances)

        storage_vm_instance_ids = [vm["uuid"] for vm in vm_instances]

        # Create all element managers that are not running
        self.logger.debug("Creating new Element-Managers")
        for vm_instance_id in storage_vm_instance_ids:
            if vm_instance_id not in self.vm_instances:
                self.logger.debug("Creating Element-Manager for VM instance id " + str(vm_instance_id))
                self.new_vm_instance(vm_instance_id=vm_instance_id)

        # Delete all managers that are not listed in storage anymore
        self.logger.debug("Deleting old Element-Managers")
        vm_instance_ids_to_delete = []
        for vm_instance_id in self.vm_instances:
            if vm_instance_id not in storage_vm_instance_ids:
                self.logger.debug("Deleting Element-Manager for VM instance id " + str(vm_instance_id))
                self.vm_instances[vm_instance_id].stop()
                vm_instance_ids_to_delete.append(vm_instance_id)
                self.vm_instances.pop(vm_instance_id)

        # Remove entries from dictionary
        for vm_instance_id in vm_instance_ids_to_delete:
            self.managers.pop(vm_instance_id)

        return True

    def stop(self):

        for id, vm in self.vm_instances.items():
            vm.stop()
        self.vm_instances = None
        self.rpc.deregister(self.routing_key + ".new_vm_instance")





