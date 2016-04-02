##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_utils_components import PluginInterface, In, Out


class VNFManager(object):
    """
    A VNFManager controls the lifecycle of a given VNF.

    A VNF can either be a be single VM, a group of VMs of the same kind or an arbitrary set of VMs.

    This openess ensures comparability with the ETSI Standard
    """

    __metaclass__ = PluginInterface


    def update_vnf(self, *args, **kwargs):
        pass

    def upgrade_vnf(self, *args, **kwargs):
        pass

    def check_vnf(self, *args, **kwargs):
        pass

    def get_state(self, *args, **kwargs):
        pass

    @In("interface", str)
    @In("ip_address", str)
    @Out("ack", bool)
    def add_successor(self, *args,**kwargs):
        pass

    @In("interface", str)
    @In("ip_address", str)
    @Out("ack", bool)
    def add_predecessor(self, *args,**kwargs):
        pass

    @In("vm_instance_id", unicode)
    @Out("ack", bool)
    def new_vm_instance(self, vm_instance_id):
        pass

    def scale_up(self, *args, **kwargs):
        """
        Shuts down the old instance and starts a new one on better hardware

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def scale_down(self, *args, **kwargs):
        """
        Shuts down the old instance and starts a new one on worse hardware

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def scale_in(self, *args, **kwargs):
        """
        Terminates an instance.

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def scale_out(self, *args, **kwargs):
        """
        Start a new instance.

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def pause(self, *args, **kwargs):
        pass

    def shutdown(self, *args, **kwargs):
        pass

    def on_vm_action(self, *args, **kwargs):
        pass

    @In("interface", str)
    @In("ip_address", str)
    @Out("ack", bool)
    def on_neighbor_action(self):
        pass

    def on_vnf_action(self):
        pass