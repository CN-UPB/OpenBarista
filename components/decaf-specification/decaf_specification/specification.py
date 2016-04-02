#!/usr/bin/env python

# Copyright 2016 DECaF Project Group
# This file is part of the DECaF project and originally derives from OpenMANO nfvo.py

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
from decaf_utils_components.base_daemon import daemonize
from docutils.nodes import image

import json
import yaml
from jsonschema import validate as js_v, ValidationError as js_vError
import auxiliary_functions as af
from schemas.scenario_schema import *
from schemas.vnf_schema import *
import os
import twisted.internet.defer as defer

from decaf_utils_components import BasePlugin, In, Out
import decaf_storage

__author__ = 'Sergio, Djoum'

global global_config
global_config = {}
global_config['vnf_repository'] = '/tmp/decaf'

"""
    - parse a yaml file and transforms it into either
        vnfd data structure or nsd data structure
    - validate the generated data structure depending on the given schema

    :param filepath this is the path to the file
    :param schema to validate the generated data structure

    :return 1, nsd if the data structure is of the type NS descriptor
    :return 2, vnfd if the data structure is of the type VNF descriptor
    :return -1, None if the parsing failed
"""


class Specification(BasePlugin):
    __version__ = "0.1-dev01"

    def __init__(self, logger=None, config=None):
        super(Specification, self).__init__(logger=logger, config=config)

    def _after_connect(self):
        self.s = decaf_storage.Endpoint(self.rpc, self.logger)

    def _check_descriptor(self, filePath):
        """
        Check whether the descriptor provided in the filepath is valid and convert into a json string.
        This method has been taken from OpenMANO and a little modified.
        We should not reinvent the wheel.

        :param filePath: File path of the descriptor.
        :return: The descriptor as a JSON String.
        """

        readFile = file(filePath, "r")
        descriptor = readFile.read()
        readFile.close()

        if 'topology' in descriptor:
            self.logger.info("This is a network scenario description")
            # TODO : convert the yaml file to json and verify if the structure of the json file match the nsd schema
            # convert the yaml string into json string
            nsd = yaml.load(descriptor)
            self.logger.debug(nsd)
            try:
                js_v(nsd, nsd_schema)
                # pass

            except js_vError as e:
                self.logger.debug("Parsing: Error validation, make sure that your file contains " \
                                  "all required fields or that the description file corresponds to the schema and vis versa")
                self.logger.debug(e)
                return -1, None
            return 1, nsd
        else:
            if 'vnf' in descriptor:
                self.logger.debug("This is a vnf descriptor")
                vnfd = yaml.load(descriptor)
                try:
                    js_v(vnfd, vnfd_schema_v01)
                    # pass
                except js_vError as e:
                    self.logger.debug("Parsing: Error validation, make sure that your file contains " \
                                      "all required fields or that the description file corresponds to the schema and vis versa")
                    self.logger.debug(e)
                    return -1, None
                return 2, vnfd
            else:
                self.logger.debug("Parsing: This is a wrong file, please give the right one")
                return -1, None

    def parseFlavorFromVNFC(self, vnfc):
        """
        Retrieve a flavor from a VNFC Dictionary.

        :param vnfc: VNFC Dictionary.
        :return: Flavor's dictionary.
        """
        myflavorDict = {}
        myflavorDict["name"] = vnfc['name'] + "-flv"
        myflavorDict["description"] = vnfc.get("description", 'VM %s of the VNF %s' % (vnfc['name'], vnfc['name']))
        myflavorDict["ram"] = vnfc.get("ram", 0)
        myflavorDict["vcpus"] = vnfc.get("vcpus", 0)
        myflavorDict["disk"] = vnfc.get("disk", 0)

        return myflavorDict

    def parseImageFromVNFC(self, vnfc):
        """
        Retrieve an image from a VNFC Dictionary.

        :param vnfc: VNFC Dictionary.
        :return: Image's dictionary.
        """
        image_dict = {
            'location': vnfc['VNFC image'],
            'name': vnfc['name'] + "-img",
            'description': 'Image of the VNFC %s' % (vnfc['name'])
        }
        return image_dict

    @In("filePath", str)
    @Out("vnf_id", str)
    def new_vnf(self, filepath):
        """
        Create a new VNF in the storage based on a descriptor.

        :param filepath: Path of the file containing the VNF Descriptor.
        :return: VNF ID.
        """

        global global_config

        rollback = list()

        nfvo_tenant = None
        res, vnf_descriptor = self._check_descriptor(filePath=filepath)

        print vnf_descriptor['vnf']['VNFC']

        # Check whether the vnf is already existing in the repository
        result, message = self.check_vnf_descriptor(vnf_descriptor)
        if result < 0:
            self.logger.debug("new_vnf error: %s" % message)
            print "new_vnf error: %s" % message
            return "VNF de: %s" % message

        # Assigning default values
        vnf_name = vnf_descriptor['vnf']['name']
        vnf_descriptor['vnf']['description'] = vnf_descriptor['vnf'].get("description", vnf_name)
        vnf_descriptor['vnf']['public'] = vnf_descriptor['vnf'].get("public", True)
        vnf_descriptor['vnf']['max_instance'] = vnf_descriptor['vnf'].get("max_instance", 1)

        # From OpenMano
        if len(vnf_descriptor['vnf']['VNFC']) > 1:
            internal_connections = vnf_descriptor['vnf'].get('internal_connections', [])
            for ic in internal_connections:
                if len(ic['elements']) > 2 and ic['type'] == 'ptp':
                    defer.returnValue(
                        "Mismatch 'type':'ptp' with %d elements at 'vnf':'internal-conections'['name':'%s']. Change 'type' to 'data'" % (
                        len(ic), ic['name']))
                elif len(ic['elements']) == 2 and ic['type'] == 'data':
                    defer.returnValue(
                        "Mismatch 'type':'data' with 2 elements at 'vnf':'internal-conections'['name':'%s']. Change 'type' to 'ptp'" % (
                        ic['name']))

        # For each VNFC, we add it to the VNFCDict and we create a flavor.
        VNFCDict = {}
        try:
            self.logger.debug('Adding flavor ...')
            for vnfc in vnf_descriptor['vnf']['VNFC']:
                VNFCitem = {}
                VNFCitem["name"] = vnfc['name']
                VNFCitem["description"] = vnfc.get("description", 'VM %s of the VNF %s' % (vnfc['name'], vnf_name))

                # we add the flavor in the database
                myflavorDict = self.parseFlavorFromVNFC(vnfc)
                self.logger.debug(myflavorDict)

                flavuuid = ''
                try:
                    flavuuid = self.s.add("flavor", data=myflavorDict)
                except Exception as err:
                    self.logger.exception(err)
                self.logger.debug('Flavor added: %s' % (flavuuid))
                rollback.append({'flavor': flavuuid})

                image_dict = {'location': vnfc['VNFC image'], 'name': vnfc['name'] + "-img",
                              'description': 'Image of the VNFC %s' % (vnfc['name']),
                              'username': vnfc['auth']['username'],
                              'password': vnfc['auth']['password']
                              }

                imguuid = ''
                try:
                    imguuid = self.s.add("image", data=image_dict)
                except Exception as err:
                    self.logger.exception(err)
                self.logger.debug('Image added', imguuid)
                rollback.append({'image': imguuid})

                VNFCitem["image_id"] = imguuid
                VNFCitem["image_path"] = vnfc['VNFC image']

                VNFCitem["flavor_id"] = flavuuid
                VNFCitem["max_instance"] = vnfc.get("max_instance", 1)
                VNFCitem["events"] = vnfc.get("events", dict())
                VNFCitem["files"] = vnfc.get("files", dict())
                VNFCDict[vnfc['name']] = VNFCitem

            self.logger.debug('Adding images ...')

        except KeyError as e:
            self.logger.debug("Error while creating a VNF. KeyError: " + str(e))
            defer.returnValue("Error while creating a VNF. KeyError " + str(e))

        # Step 4. Storing the VNF in the repository
        self.logger.debug("Storing YAML file of the VNF")
        vnf_descriptor_filename = global_config['vnf_repository'] + "/" + vnf_name + ".vnfd"

        self.logger.debug(vnf_descriptor_filename)

        vnf_id = self.__add_vnf(vnf_name, vnf_descriptor,
                                vnf_descriptor_filename, nfvo_tenant, VNFCDict, )

        self.logger.debug('VNF saved: ', vnf_id)

        return vnf_id

    def __rollback(self, to_roll):

        for v in to_roll.reverse():
            table, uuid_ = v.items()
            self.s.delete(table, uuid=uuid_)

    def delete_flavor(self, flavor_id):
        """
        Delete a flavor from the database.

        :param flavor_id: Uuid of the flavor to delete.
        :return: True, if the flavor has been deleted and otherwise false.
        """
        pass

    def delete_image(self, image_id):
        """
        Delete an image from the database.

        :param image_id: Uuid of the image to delete.
        :return: True, if the image has been deleted and otherwise false.
        """
        pass

    def alter_flavor(self, flavor_id, **kwargs):
        """
        Modify the flavor specification.

        :param flavor_id: Uuid of the flavor to alter.
        :param kwargs: New flavor's information provided in form of a dictionary.
        :return: True, if the flavor has been altered and otherwise false.
        """
        pass

    def alter_image(self, image_id, **kwargs):
        """
        Modify the image specification.

        :param image_id: Uuid of the image to alter.
        :param kwargs: New image's information provided in form of a dictionary.
        :return: True, if the image has been altered and otherwise false.
        """
        pass

    def delete_vnf_edge(self, vnf_id, net_id):
        """
        Delete an edge inside a VNF.

        :param vnf_id: Uuid of the VNF in which the edge has to be modified.
        :param net_id: Uuid of the edge to delete.
        :return: True, if the edge has been deleted and otherwise false.
        """
        pass

    def delete_scenario_edge(self, sce_id, sce_net_id):
        """
        Delete an edge inside a scenario, that is the link between two VNFs

        :param sce_id: Uuid of the scenario in which the edge has to be modified.
        :param sce_net_id: Uuid of the edge to delete.
        :return: True, if the edge has been deleted and otherwise false.
        """
        pass

    def alter_scenario(self, sce_id, scenario_graph):
        """
        Modify the image specification.

        :param sce_id: Uuid of the scenario to alter.
        :param scenario_graph: New scenario's information provided in form of a dictionary.
        :return: True, if the scenario has been altered and otherwise false.
        """
        pass

    def alter_vnf(self, vnf_id, vnf_graph):
        """
        Modify the image specification.

        :param vnf_id: Uuid of the VNF to alter.
        :param vnf_graph: New vnf's information provided in form of a dictionary.
        :return: True, if the VNF has been altered and otherwise false.
        """
        pass

    'Hi Sergio, I wrote this. After the demo we can put this somewhere else ! Regards Thorsten '

    @defer.inlineCallbacks
    def create_new_manager(self, *args, **kwargs):
        whatever = yield self.daemon.bunny_connector.rpc.call("VNFManagerAdapter.create_vnf_manager", *args, **kwargs)

    @In("vnf_id", str)
    @In("scenario_id", str)
    @Out("code", int)
    @Out("message", str)
    def delete_vnf(self, vnf_id, scenario_id):
        """
        Delete a VNF that belongs to a scenario.

        :param vnf_id: Uuid of the VNF to delete.
        :param scenario_id: Uuid of the scenario in which the VNF should be deleted.
        :return: Either a pair (200, message) in case where the process worked or (500, error_message) otherwise.
        """

        # 1. Check whether the given scenario is existing
        scen = self.s.get("scenario", filters={'uuid': scenario_id}, options=[])
        if len(scen) == 0:
            self.logger.debug('The scenario with the ID: %s is not existing in the repository', (scenario_id))
            return 500, 'The scenario with the ID: %s is not existing in the repository', (scenario_id)

        # 2. Check whether the given VNF is existing

        vnf = self.s.get("vnf", filters={'uuid': vnf_id}, options=[])
        if len(vnf) == 0:
            self.logger.debug('The VNF with the ID: %s is not existing in the repository', (vnf_id))
            return 500, 'The scenario with the ID: %s is not existing in the repository', (vnf_id)

        # 3. Check whether the VNF is contained in the scenario

        match = self.s.get("scenario_vnf", filters={'scenario_id': scenario_id, 'vnf_id': vnf_id}, options=[])
        if len(match) == 0:
            self.logger.debug('The VNF with the ID %s is not existing in the scenario with the ID: %s',
                              (vnf_id, scenario_id))
            return 500, 'The VNF with the ID %s is not existing in the scenario with the ID: %s', (vnf_id, scenario_id)

            # 4. Check whether an instance of this scenario is existing
            # If it is the case then, we must not delete, rather we can propose a solution
        instances = self.s.get("scenario_instance", filters={'scenario_id': scenario_id}, options=[])
        nbInst = len(instances)
        if nbInst > 0:
            self.logger.debug(
                'Exactly %d instance(s) of this scenario model have been deployed and might be running in the VIM',
                (nbInst))
            return 500, 'Exactly %d instance(s) of this scenario model have been deployed and might be running in the VIM', (
            nbInst)

        # 5. Start the process of deleting
        # a. Delete Scenario interfaces
        sce_net_list = self.__del_vnf_interface(scenario_id, vnf_id)

        if not isinstance(sce_net_list, list):
            self.logger.debug("error while deleting scenario_interfaces")
            return 500

        self.logger.debug("scenario net list", sce_net_list)

        # b. get all vms of this VNF
        self.logger.debug("get all vms of this VNF")
        vms = self.s.get("vm", options=['interfaces'], filters={'vnf_id': vnf_id})
        if len(vms) == 0:
            self.logger.error("An error has occured while getting scenario_vnf in the database. scenario_vnf not found")
            return 500

        for vm in vms:
            for inter in vm['interfaces']:
                self.s.delete("interface", uuid=inter['uuid'])

        # 4. delete all internal nets of the VNF (nets)
        self.__del_net(vnf_id)

        self.logger.debug("Internal nets deleted if existing")

        # 5.delete all vms of the VNF

        self.logger.debug(vms)

        for vm in vms:
            self.logger.debug(vm)
            self.s.delete("vm", uuid=vm['uuid'])

        # 6. delete scenario_vnf
        self.s.delete("scenario_vnf", uuid=match[0]['uuid'])

        # 7. delete the VNF
        self.s.delete("vnf", uuid=vnf_id)

        # 8. delete scenario nets this part is a bit complicated
        # since we should delete interface involved in these scenario_nets
        for sce_net in sce_net_list:
            sce_int = self.s.get('scenario_interface', options=[], filters={'scenario_net_id': sce_net})
            if len(sce_int) == 0:
                self.logger.error("An error has occured while getting scenario_interface in the database")
                return 500, "An error has occured while getting scenario_interface in the database"
            for inter in sce_int:
                self.s.delete("scenario_interface", uuid=inter['uuid'])

        return 200, ("VNF %s has been deleted" % (vnf_id))

    @In('scenario_id', str)
    @Out('code', int)
    @Out('message', str)
    def delete_scenario(self, scenario_id):
        """
        Delete a scenario. This method checks whether there is an instance which is based on this scenario model before starting the deleting process.

        :param scenario_id: Uuid of the scenario to delete.
        :return: Either a pair (200, message) in case where the process worked or (500, error_message) otherwise.
        """

        # 1. Check whether the given scenario is existing
        scen = self.s.get("scenario", filters={'uuid': scenario_id}, options=[])
        if len(scen) == 0:
            self.logger.debug('The scenario with the ID: %s is not existing in the repository', (scenario_id))
            return 500, 'The scenario with the ID: %s is not existing in the repository', (scenario_id)

        scenario_vnfs = self.s.get("scenario_vnf", filters={'scenario_id': scenario_id}, options=[])
        if len(scenario_vnfs) == 0:
            self.logger.debug('There is no VNF in the scenario %s', (scenario_id))
            return 500, 'There is no VNF in the scenario %s', (scenario_id)
        self.logger.debug("Start deleting VNFs")
        for sce_vnf in scenario_vnfs:
            self.logger.debug("Start deleting VNF %s" % (sce_vnf['vnf_id']))
            self.delete_vnf(sce_vnf['vnf_id'], scenario_id)

        sce_nets = self.s.get('scenario_net', options=[], filters={'scenario_id': scenario_id})

        if len(sce_nets) == 0:
            self.logger.debug('There is no scenario net in this scenario. !!Strange!!')
            return 500, 'There is no scenario net in this scenario. !!Strange!!'

        for sce_net in sce_nets:
            self.s.delete("scenario_net", uuid=sce_net['uuid'])

        self.s.delete("scenario", uuid=scenario_id)

        return 200, ("The scenario with ID %s has been deleted" % (scenario_id))

    def __del_net(self, vnf_id):
        """
        Delete all edges inside a VNF.

        :param vnf_id: Uuid of the VNF in which the edges have to be deleted.
        :return:
        """
        nets = self.s.get('net', options=[], filters={'vnf_id': vnf_id})

        if len(nets) == 0:
            self.logger.info("There is no net inside this vnf")
        else:
            for net in nets:
                self.s.delete("net", uuid=net['uuid'])

    def __del_vnf_interface(self, scenario_id, vnf_id):
        """
        Delete interfaces related to a VNF.

        :param scenario_id: Uuid of the scenario in which the VNF belongs to.
        :param vnf_id: Uuid of the VNF in which interfaces have to be deleted.
        :return: A list of scenario nets.
        """

        sce_net_list = list()

        scenario_vnf = self.s.get('scenario_vnf', options=[],
                                  filters={'scenario_id': scenario_id,
                                           'vnf_id': vnf_id})

        scenario_vnf_id = scenario_vnf[0]['uuid']
        # get all scenario interfaces
        sce_interfaces = self.s.get('scenario_interface', options=[], filters={'scenario_vnf_id': scenario_vnf_id})

        if len(sce_interfaces) == 0:
            self.logger.error("An error has occured. There is no scenario interface")
            return list()

        for sce_int in sce_interfaces:
            self.logger.debug(sce_int)
            sce_net_list.append(sce_int['scenario_net_id'])
            self.s.delete('scenario_interface', uuid=sce_int['uuid'])

        return sce_net_list

    def check_vnf_descriptor(self, vnf_descriptor):
        """
        Check whether the vnf descriptor is existing in the VNF repository.

        :param vnf_descriptor:
        :return:
        """
        global global_config
        # TODO:
        vnf_filename = global_config['vnf_repository'] + "/" + vnf_descriptor['vnf']['name'] + ".vnfd"
        if os.path.exists(vnf_filename):
            self.logger.debug("WARNING: The VNF descriptor already exists in the VNF repository")
            return 500, "WARNING: The VNF descriptor already exists in the VNF repository"
        return 200, None

    def __add_vnf(self, vnf_name, vnf_descriptor, vnf_descriptor_filename, nfvo_tenant, VNFCDict):
        """
        Add a VNF and its relatives in the storage component.

        :param vnf_name: Name of the VNF.
        :param vnf_descriptor: Descriptor of the VNF. It contains all info related to this VNF.
        :param vnf_descriptor_filename: File name of the descriptor. It will be stored in the local repository.
        :param nfvo_tenant: Tenant ID. This will be used for future implementation steps.
        :param VNFCDict: VNFC Dictionary. It contains information of all VNFC related to this VNF.
        :return: return the uuid of the created VNF.
        """
        myVNFDict = {}
        myVNFDict["name"] = vnf_name
        myVNFDict["path"] = vnf_descriptor_filename
        myVNFDict["public"] = vnf_descriptor['vnf']['public']
        myVNFDict["description"] = vnf_descriptor['vnf']['description']
        myVNFDict["max_instance"] = vnf_descriptor['vnf']['max_instance']

        try:
            vnf_id = self.s.add("vnf", data=myVNFDict)
        except Exception as err:
            self.logger.exception(err)

        self.logger.debug("VNF %s added to the storage component. VNF id: %s" % (vnf_name, vnf_id))

        self.logger.debug("Adding new vms to the storage")
        # For each vm, we must create the appropriate vm in the NFVO database.
        vmDict = self.__add_vms(VNFCDict, nfvo_tenant, vnf_id)

        net_id = self.__add_nets_and_interfaces(vnf_descriptor, nfvo_tenant, vmDict, vnf_id)
        return vnf_id

    def __add_vms(self, VNFCDict, nfvo_tenant, vnf_id):
        """
        Add all VFNC of a VNF in the storage.

        :param VNFCDict: VNFC Dictionary. It contains information of all VNFC related to this VNF.
        :param nfvo_tenant: Tenant ID. This will be used for future implementation steps.
        :param vnf_id: the ID of the VNF.
        :return: VNFC Dictionary. It contains IDs of all created VNFC.
        """
        vmDict = {}
        for _, vm in VNFCDict.iteritems():
            self.logger.debug("VM name: %s. Description: %s" % (vm['name'], vm['description']))
            vm["vnf_id"] = vnf_id

            self.logger.debug("test %s " % (vm))

            try:
                vm_id = self.s.add("vm", data=vm)
            except Exception as err:
                self.logger.exception(err)

            self.logger.debug("Internal vm id in storage: %s" % vm_id)
            vmDict[vm['name']] = vm_id

        return vmDict

    def __add_nets_and_interfaces(self, vnf_descriptor, nfvo_tenant, vmDict, vnf_id):
        """
        Create nets and interface of all VNFC of the VNF.

        :param vnf_descriptor: Descriptor of the VNF.
        :param nfvo_tenant: nfvo_tenant: Tenant ID. This will be used for future implementation steps.
        :param vmDict: Dictionary containing all VM IDs.
        :param vnf_id: ID of the current VNF.
        :return:
        """
        net_id = 0
        # Collect the data interfaces of each VM/VNFC under the 'numas' field
        dataifacesDict = {}
        for vnfc in vnf_descriptor['vnf']['VNFC']:
            if 'data-ifaces' in vnfc:
                dataifacesDict[vnfc['name']] = {}
                for dataiface in vnfc['data-ifaces']:
                    af.convert_bandwidth(dataiface)
                    dataifacesDict[vnfc['name']][dataiface['name']] = {}
                    dataifacesDict[vnfc['name']][dataiface['name']]['vpci'] = dataiface['vpci']
                    dataifacesDict[vnfc['name']][dataiface['name']]['bw'] = dataiface['bandwidth']

        # Collect the bridge interfaces of each VM/VNFC under the 'bridge-ifaces' field
        bridgeInterfacesDict = {}
        for vnfc in vnf_descriptor['vnf']['VNFC']:
            if 'bridge-ifaces' in vnfc:
                bridgeInterfacesDict[vnfc['name']] = {}
                for bridgeiface in vnfc['bridge-ifaces']:
                    af.convert_bandwidth(bridgeiface)
                    bridgeInterfacesDict[vnfc['name']][bridgeiface['name']] = {}
                    bridgeInterfacesDict[vnfc['name']][bridgeiface['name']]['vpci'] = bridgeiface.get('vpci', None)
                    bridgeInterfacesDict[vnfc['name']][bridgeiface['name']]['bw'] = bridgeiface.get('bandwidth', None)

        # For each internal connection, we add it to the interfaceDict and we  create the appropriate net in the NFVO database.
        self.logger.debug("Adding new nets (VNF internal nets) to the NFVO database (if any)")
        internalconnList = []
        if 'internal-connections' in vnf_descriptor['vnf']:
            for net in vnf_descriptor['vnf']['internal-connections']:
                self.logger.debug("Net name: %s. Description: %s" % (net['name'], net['description']))

                myNetDict = {}
                myNetDict["name"] = net['name']
                myNetDict["description"] = net['description']
                # myNetDict["type"] = net['type']
                myNetDict["vnf_id"] = vnf_id

                # net_id = self.add_net(myNetDict)
                try:
                    net_id = self.s.add("net", data=myNetDict)
                except Exception as err:
                    self.logger.exception(err)

                self.logger.debug("net created: %s" % (net_id))

                for element in net['elements']:
                    ifaceItem = {}
                    # ifaceItem["internal_name"] = "%s-%s-%s" % (net['name'],element['VNFC'], element['local_iface_name'])
                    ifaceItem["internal_name"] = element['local_iface_name']
                    ifaceItem["external_name"] = '-'
                    ifaceItem["vm_id"] = vmDict[element['VNFC']]
                    ifaceItem["net_id"] = net_id
                    ifaceItem["type"] = net['type']
                    if ifaceItem["type"] == "data":
                        ifaceItem["vpci"] = dataifacesDict[element['VNFC']][element['local_iface_name']]['vpci']
                        ifaceItem["bw"] = dataifacesDict[element['VNFC']][element['local_iface_name']]['bw']
                    else:
                        ifaceItem["vpci"] = bridgeInterfacesDict[element['VNFC']][element['local_iface_name']]['vpci']
                        ifaceItem["bw"] = bridgeInterfacesDict[element['VNFC']][element['local_iface_name']]['bw']
                    internalconnList.append(ifaceItem)

                self.logger.debug("Internal net id in NFVO DB: %s" % net_id)

        self.logger.debug("Adding internal interfaces to the NFVO database (if any)")
        for iface in internalconnList:
            self.logger.debug("Iface name: %s" % iface['internal_name'])
            try:
                iface_id = self.s.add("interface", data=iface)
            except Exception as err:
                self.logger.exception(err)

            self.logger.debug("Iface id in NFVO DB: %s" % iface_id)

        self.logger.debug("Adding external interfaces to the NFVO database")
        for iface in vnf_descriptor['vnf']['external-connections']:
            myIfaceDict = {}
            myIfaceDict["internal_name"] = iface['local_iface_name']
            myIfaceDict["vm_id"] = vmDict[iface['VNFC']]
            myIfaceDict["external_name"] = iface['name']
            myIfaceDict["type"] = iface['type']
            if iface["type"] == "data":
                myIfaceDict["vpci"] = dataifacesDict[iface['VNFC']][iface['local_iface_name']]['vpci']
                myIfaceDict["bw"] = dataifacesDict[iface['VNFC']][iface['local_iface_name']]['bw']
            else:
                myIfaceDict["vpci"] = bridgeInterfacesDict[iface['VNFC']][iface['local_iface_name']]['vpci']
                myIfaceDict["bw"] = bridgeInterfacesDict[iface['VNFC']][iface['local_iface_name']]['bw']
            self.logger.debug("Iface name: %s" % iface['name'])

            try:
                iface_id = self.s.add("interface", data=myIfaceDict)
            except Exception as err:
                self.logger.exception(err)

            self.logger.debug("Iface id in NFVO DB: %s" % iface_id)

        self.logger.debug("Net ID: ", net_id)
        return net_id

    def check_vnf_descriptor(self, vnf_descriptor):
        """
        Check whether the vnf has been stored into the catalog.

        :param vnf_descriptor:
        :return:
        """
        global global_config
        vnf_filename = global_config['vnf_repository'] + "/" + vnf_descriptor['vnf']['name'] + ".vnfd"
        if os.path.exists(vnf_filename):
            print "WARNING: The VNF descriptor already exists in the VNF repository"
            return -200, "Error"
        return 200, None

    def get_vms_vnf(self, vnf_id):

        code, vnfObject = self.s.get("vnf", filters={'uuid': vnf_id}, options=['vms'])
        return vnfObject

    def __get_interfaces_vnf(self, vnf_id):
        """
        Get all external interfaces of a vnf. The idea is to get all vms it is related with and for each vm return its external interfaces.

        :param vnf_id: Uuid of the VNF in which the interfaces should be retrieved.
        :return: Code given by the storage component and also result I obtained.
        """

        vnfs = self.s.get("vnf", filters={'uuid': vnf_id}, options=['vms'])
        if (len(vnfs) == 0):
            return 'Error in getting VMs in the database, please look at the log'

        vnf = vnfs[0]
        self.logger.info("#####################################")
        self.logger.info(vnf)
        self.logger.info("#####################################")

        vms = vnf['vms']

        # for each vm in vms, get its uuid, query all external interfaces it gets
        # And save them in a new dictionary
        ifaces = []
        i = 0
        for vm in vms:
            self.logger.info('VM VM VM VM VM Vm')
            self.logger.info('vm_id: ', vm['uuid'])
            interfaces = self.s.get("interface", filters={'vm_id': vm['uuid']}, options=[])
            self.logger.info("###############Interfaces######################")
            self.logger.info(interfaces)
            self.logger.info("################End interfaces#####################")
            for iface in interfaces:
                self.logger.info("###############Iface######################")
                self.logger.info(iface)
                self.logger.info("################End iface#####################")
                if iface['net_id'] == None:
                    self.logger.info('-------------------')
                    # ifaces.insert(i, iface['external_name'])
                    ifaces.insert(i, iface)
                    self.logger.info(iface)
                    i = i + 1

        self.logger.info(ifaces)

        return ifaces

    def __check_vnf(self, vnf_id):

        self.logger.debug("Test: ", vnf_id)
        vnfs = self.s.get("vnf", options=[], filters={'uuid': vnf_id})
        if (len(vnfs) == 0):
            return 'Error in getting VMs in the database, please look at the log'
        return vnfs[0]

    @In('filePath', str)
    @In('id_map', dict)
    @Out('scenario_id', str)
    def new_scenario(self, filepath, **id_map):
        """
        Create a new scenario in the storage

        :param filepath: Path of the descriptor file
        :param id_map:
        :return: scenario ID
        """

        # interfaces = yield self.get_interfaces_vnf('4cada0b4-02ac-4c19-8345-a1c21fa67ad9')

        self.logger.debug('validating the descriptor')
        res, topo = self._check_descriptor(filePath=filepath)
        if res < 0:
            self.logger.debug('Validation error');
            # defer.returnValue('Validation error')
            return 'The descriptor component could not be verified'

        self.logger.debug('Descriptor validated %s' % (topo));

        vnfs = {}
        nodes = topo['topology']['nodes']
        for k in nodes.keys():
            if nodes[k]['type'] == 'VNF':
                vnfs[k] = nodes[k]
                vnfs[k]['ifaces'] = {}

        # ============================= Nodes ===============================
        ifaces = {}
        VNFDict = {}
        for name, vnf in vnfs.items():
            vnf_id = None

            if 'uuid' not in vnf:
                vnf["uuid"] = id_map.get(vnf["name"], None)
            else:
                vnf["uuid"] = id_map.get(vnf["VNF model"], vnf["uuid"])

            if not vnf["uuid"]:
                return 'Please give the uuid in the specification'

            self.logger.debug("Checking whether the vnf is existing in the database")
            vnfInfo = self.__check_vnf(vnf['uuid'])

            self.logger.debug(vnfInfo)

            if vnfInfo == None:
                self.logger.debug('Error in getting the VNf info. Please make sure the uuid you provided is correct')
                return 'Error in getting the VNf info. Please make sure the uuid you provided is correct'

            self.logger.debug("VNF in the database ...")
            # Take the list of
            VNFDict[name] = {}
            VNFDict[name]['name'] = vnfInfo['name']
            VNFDict[name]['uuid'] = vnfInfo['uuid']
            VNFDict[name]['type'] = vnf['type']

            ext_ifaces = self.__get_interfaces_vnf(vnfInfo['uuid'])
            self.logger.info('Adding external interfaces in the dictionary \n ')
            self.logger.info(ext_ifaces)

            if ext_ifaces == None:
                return 'The VNF with the uuid: %s should have at leat one external interface' % (name)

            VNFDict[name]['ifaces'] = {}

            self.logger.info('Adding external interfaces in the dictionary \n ')
            for ext in ext_ifaces:
                self.logger.info(ext)
                VNFDict[name]['ifaces'][ext['external_name']] = ext
                self.logger.info('\n')

        self.logger.info('\n')
        self.logger.info('VNFDict')
        self.logger.info(VNFDict)

        connections = topo['topology']['connections']
        self.logger.info('\n')
        self.logger.info('\n')
        self.logger.info('\n')
        self.logger.debug('connections')
        self.logger.info(connections)

        connections_list = []
        for k in connections.keys():
            ifaces_list = []
            if 'nodes' not in connections[k]:
                continue
            conection_pair_list = map(lambda x: x.items(), connections[k]['nodes'])
            for k2 in conection_pair_list:
                ifaces_list += k2
            connections_list.append(set(ifaces_list))

        # This part is used to unify the connection list. This means that if an interface appears twice
        # in the descriptor then it should be consider as one.
        index = 0
        while index < len(connections_list):
            index2 = index + 1
            while index2 < len(connections_list):
                if len(connections_list[index] & connections_list[index2]) > 0:  # common interface, join nets
                    connections_list[index] |= connections_list[index2]
                    del connections_list[index2]
                else:
                    index2 += 1
            connections_list[index] = list(connections_list[index])  # from set to list again
            index += 1

        self.logger.info('\n')
        self.logger.info('\n')
        # self.logger.info(connections_list)
        self.logger.debug("testlog")
        self.logger.info('\n ---- ')

        # Check whether the interfaces match with those in the vnf
        self.logger.info('For each connection in connection list')
        for con in connections_list:
            for node, iface in con:
                nodeInfo = VNFDict[node]
                ifaces = nodeInfo['ifaces']
                self.logger.debug('node: ', node)
                self.logger.debug('ifaces: ', ifaces)
                self.logger.debug('iface: ', iface)
                if iface not in nodeInfo['ifaces']:
                    return 'The iface %s does not exist in the VNF %s' % (iface, nodeInfo['name'])

        scenarioInfo = {}
        scenarioInfo['name'] = topo['name']
        scenarioInfo['description'] = topo['description']

        # Add the scenario in the database
        try:
            scenario_id = self.s.add("scenario", data=scenarioInfo)
        except Exception as err:
            self.logger.exception(err)

        # Add related VNF in the database
        for k in VNFDict.keys():
            scenario_vnf = {}
            scenario_vnf['scenario_id'] = scenario_id
            scenario_vnf['vnf_id'] = VNFDict[k]['uuid']
            try:
                scenario_vnf_id = self.s.add("scenario_vnf", data=scenario_vnf)
            except Exception as err:
                self.logger.exception(err)

            VNFDict[k]['scenario_vnf_id'] = scenario_vnf_id

        self.logger.info('New VNFDIct after adding the related VNFs')
        self.logger.info(VNFDict)

        try:
            # add public interfaces
            public_int = connections['public_interfaces']

            pairs = map(lambda x: x.items(), public_int)

            for pair in pairs:

                # For each public interface create a net
                conDict = {}
                conDict['name'] = k
                conDict['scenario_id'] = scenario_id

                self.logger.info('adding the net : %s for pair %s of public interface' % (conDict, pair))

                try:
                    net_id = self.s.add("scenario_net", data=conDict)
                except Exception as err:
                    self.logger.exception(err)

                ifaces = VNFDict[pair[0][0]]['ifaces']
                iface_id = None
                for i in ifaces.keys():
                    self.logger.info('found interface')
                    self.logger.info(i)
                    if pair[0][1] == i:
                        iface_id = ifaces[i]['uuid']
                        self.logger.info(iface_id)
                        break
                uuid = VNFDict[pair[0][0]]['uuid']
                scenario_iface = {}

                scenario_iface['scenario_vnf_id'] = VNFDict[pair[0][0]]['scenario_vnf_id']
                scenario_iface['scenario_net_id'] = net_id
                scenario_iface['interface_id'] = iface_id
                scenario_iface['public'] = True
                self.logger.info('adding the public interface in scenario interface')
                try:
                    id = self.s.add("scenario_interface", data=scenario_iface)
                except Exception as err:
                    self.logger.exception(err)

                self.logger.info('added the public interface with id: %s in scenario interface' % (id))

        except Exception as e:
            self.logger.debug('error in adding public interface')
            self.logger.debug(e)
            return

        # Add connections
        # This part is composed of two sub parts:
        # - Add first nets
        # - Add interfaces members of the same nets
        for k in connections.keys():

            if 'nodes' not in connections[k]:
                continue

            conDict = {}
            conDict['name'] = k
            conDict['scenario_id'] = scenario_id

            self.logger.info('add the net : %s' % (conDict))

            try:
                net_id = self.s.add("scenario_net", data=conDict)
            except Exception as err:
                self.logger.exception(err)

            # Now add ifaces
            nodes = connections[k]['nodes']
            pairs = map(lambda x: x.items(), nodes)

            self.logger.info('\n')
            self.logger.info('\n')
            self.logger.info(pairs)
            self.logger.info('\n')
            self.logger.info('\n')
            for pair in pairs:

                self.logger.info('\n')
                self.logger.info(pair)
                self.logger.info('\n')

                ifaces = VNFDict[pair[0][0]]['ifaces']
                iface_id = None
                for i in ifaces.keys():
                    self.logger.info('found interface')
                    self.logger.info(i)
                    if pair[0][1] == i:
                        iface_id = ifaces[i]['uuid']
                        self.logger.info(iface_id)
                        break
                uuid = VNFDict[pair[0][0]]['uuid']
                scenario_iface = {}

                scenario_iface['scenario_vnf_id'] = VNFDict[pair[0][0]]['scenario_vnf_id']
                scenario_iface['scenario_net_id'] = net_id
                scenario_iface['interface_id'] = iface_id
                scenario_iface['public'] = False
                self.logger.info('adding the interface')
                try:
                    id = self.s.add("scenario_interface", data=scenario_iface)
                except Exception as err:
                    self.logger.exception(err)

        return scenario_id

    @defer.inlineCallbacks
    def add_vnf_package(self, vnf_desc_file, *vnf_scipts):
        vnf_id = yield self.new_vnf(vnf_desc_file)
        for script in vnf_scipts:
            success = yield self.add_script(vnf_id, script)
        pass

    def add_script(self, vnf_id, script_file):

        script_dict = dict()
        script_dict["vnf_id"] = vnf_id
        script_dict["name"] = script_file
        script_dict["script"] = script_file

        code, uuid = yield self.daemon.bunny_connector.rpc.call("storage.add_vnf_script", data=script_dict)
        pass

    def add_scenario_package(self, scenario_desc=None, vnf_packs=None):
        pass

    @In("dir", unicode)
    @Out("id", unicode)
    def add_scenario_package_dir(self, dir=None):
        if dir:

            id_map = dict()

            for vnf_desc in os.listdir(dir + "vnfs/"):
                vnf_id = self.new_vnf(dir + "vnfs/" + vnf_desc)
                name = yaml.load(open(dir + "vnfs/" + vnf_desc, "r"))['vnf']['name']
                id_map[name] = vnf_id
            for scenario_desc in os.listdir(dir):
                if scenario_desc.endswith(".yaml"):
                    scen_ok = self.new_scenario(dir + scenario_desc, **id_map)
                    self.logger.debug(scen_ok)
                    print scen_ok
        else:
            print "Please specify a directory"
        pass


def daemon():
    daemonize(Specification)


if __name__ == '__main__':
    daemon()
