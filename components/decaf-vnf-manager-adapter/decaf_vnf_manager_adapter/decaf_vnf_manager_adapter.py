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

import sys

import os
from .ssh_vnf_manager.generic_vnf_manager import GenericSSHVNFManager
from decaf_utils_components.base_daemon import daemonize
from decaf_utils_components import PluginInterface, In, Out, BasePlugin
from decaf_storage import Endpoint as Storage


class IVNFManagerAdapter(object):
    __metaclass__ = PluginInterface


    def create_vnf_manager(self, vnf_instance_id):
        pass


class VNFManagerAdapter(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(VNFManagerAdapter, self).__init__(logger=logger, config=config)
        self.managers = dict()

    def _after_connect(self):
        self.storage = Storage(self.rpc, self.logger)
        self.update()

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass


    @In("vnf_instance_id", str)
    @Out("success", bool)
    def create_vnf_manager(self, vnf_instance_id):
        """
        Creates a VNF manager for a VNF instance.
        Can be called manually, but we suggest to use the update method instead.

        :param vnf_instance_id: The VNF instance id.
        :return: True, if successful. False otherwise.
        """

        if not self.managers.get(vnf_instance_id, None):
            try:
                self.logger.debug("Creating new VNF Manager for instance %s" % vnf_instance_id)
                self.managers[vnf_instance_id] = GenericSSHVNFManager(vnf_instance_id=vnf_instance_id, logger=self.logger)
                self.logger.debug("connecting")
                self.managers[vnf_instance_id].connect(rpc=self.rpc, routing_key=vnf_instance_id)
                self.logger.debug("VNF Manager connected")
            except BaseException as e:
                self.logger.exception(e)
                return False

        return True


    @Out("success", bool)
    def update(self):
        """
        Updates the VNF managers according to the VNF instances registered in Storage.
        Deletes managers of instances that are not registered anymore, and creates ones that are registered, but not already created.

        :return: True, if successful. False otherwise.
        """

        self.logger.debug("Updating all VNF-Managers")
        vnf_instances = self.storage.get("vnf_instance", options=[], filters={})
        self.logger.debug("Following VNFs were found: \n %s" % vnf_instances)

        storage_vnf_instance_ids = [vnf["uuid"] for vnf in vnf_instances]

        # Create all managers that are not running
        self.logger.debug("Creating new VNF-Managers")
        for vnf_instance_id in storage_vnf_instance_ids:
            if vnf_instance_id not in self.managers:
                self.logger.debug("Creating VNF-Manager for VNF instance id " + str(vnf_instance_id))
                self.create_vnf_manager(vnf_instance_id=vnf_instance_id)

        # Delete all managers that are not listed in storage anymore
        self.logger.debug("Deleting old VNF-Managers")
        vnf_instance_ids_to_delete = []
        for vnf_instance_id in self.managers:
            if vnf_instance_id not in storage_vnf_instance_ids:
                self.logger.debug("Deleting VNF-Manager for VNF instance id " + str(vnf_instance_id))
                self.managers[vnf_instance_id].stop()
                vnf_instance_ids_to_delete.append(vnf_instance_id)

        # Remove entries from dictionary
        for vnf_instance_id in vnf_instance_ids_to_delete:
            self.managers.pop(vnf_instance_id)

        return True


def daemon():

    euid = os.geteuid()
    if euid != 0:
        print "Script not started as root. Running sudo.."
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)

    print 'Running. Your euid is', euid
    daemonize(VNFManagerAdapter)

if __name__ == '__main__':
    daemon()
