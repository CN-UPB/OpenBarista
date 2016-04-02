##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

from decaf_storage import Endpoint as Storage
from decaf_utils_components import BasePlugin, In, Out
from nsenter import Namespace
import time
import os
import logging
import paramiko
import urllib2 as url
from cStringIO import StringIO
import json

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_res(path):
    return os.path.abspath(os.path.join(_ROOT, '../res', path))

class GenericSSHElementManager(BasePlugin):
    """
    Generates an ElementManager from Specification.
    """

    TIMEOUT = 20

    PING_TIMEOUT = 300

    TMP_FILE_DIR = "/tmp/decaf-vnf-manager"

    CREATE_IFACE_SCRIPT = "add_iface.sh"
    CREATE_IFACE_PYTHON = "add_iface.py"
    DELETE_IFACE_SCRIPT = "delete_iface.sh"
    DELETE_IFACE_PYTHON = "delete_iface.py"

    CREATE_IFACE_SCRIPT_REMOTE = "/tmp/decaf-vnf-manager/add_iface.sh"
    CREATE_IFACE_PYTHON_REMOTE = "/tmp/decaf-vnf-manager/add_iface.py"
    DELETE_IFACE_SCRIPT_REMOTE = "/tmp/decaf-vnf-manager/delete_iface.sh"
    DELETE_IFACE_PYTHON_REMOTE = "/tmp/decaf-vnf-manager/delete_iface.py"

    CREATE_IFACE_COMMAND = "sudo bash " + CREATE_IFACE_SCRIPT_REMOTE + " {iface_instance_id} {type} {internal} {external} {iface} {internal_or_public}"

    DELETE_IFACE_COMMAND = "sudo bash " + DELETE_IFACE_SCRIPT_REMOTE + " {iface_instance_id} {physical_iface}"

    __version__ = "0.1-dev01"

    PERMITTED_METHODS = ["after_startup",
                         "before_shutdown",
                         "new_predecessor",
                         "new_successor",
                         "delete_predecessor",
                         "delete_successor",
                         "get_status"]



    def __init__(self, vm_instance_id = None, logger=None, **kwargs):
        """
        :param host:
        :param username:
        :param password:
        :param logger:
        :return:
        """
        super(GenericSSHElementManager, self).__init__(logger=logger, config=dict())
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)

        self.host = None
        self.instance_id = vm_instance_id

        self.instance_desc = None
        self.vm_desc = None
        self.mgmt_interface_desc = None

        self.storage = None

    def _after_connect(self):

        self.logger.debug("RESOURCE PATH" + str(get_res(self.CREATE_IFACE_PYTHON)))

        self.storage = Storage(self.rpc, self.logger)

        try:
            self.instance_desc = self.storage.get("vm_instance", options=[],filters={"uuid" : self.instance_id})[0]
            self.vm_desc = self.storage.get("vm", options=[], filters={"uuid" : self.instance_desc["vm_id"]})[0]
            self.mgmt_interface_desc = self.storage.get("interface_instance", options=[], filters={"vm_instance_id" : self.instance_id, "type":"mgmt"})[0]
            self.auth = self.storage.get("vm_instance_keypair", options=[], filters={"vm_instance_id" : self.instance_id})[0]
            self.file_urls = self.instance_desc.get("files", None)
        except BaseException as e:
            self.logger.error(e)
            self.dispose()
        else:
            self.host = self.mgmt_interface_desc["ip_address"]

            if self.vm_desc["script_path"]:
                self.TMP_FILE_DIR = self.vm_desc["script_path"]

            self.logger.debug("Generating methods from script")

            if self.vm_desc["events"]:
                    self.generate_methods(self.vm_desc["events"])

            self.ssh = paramiko.SSHClient()

            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.proxy = None
            self.files = None

            pass


    @Out("success", bool )
    def connect_to_vm(self):
        """
        Starts the Element Manager and connects it to the VM. Uploads VNF manager scripts onto the machine.

        :return: True
        """

        self.logger.debug("Setup auth")
        privatekey = None
        username = None

        if self.auth:
            privatekey = self.auth["private_key"]
            if self.auth.get("username", None):
                username = self.auth["username"]
            else:
                self.logger.warning("Username not found, fallback to hardcoded one.")
                username = "debian"
        else:
            self.logger.exception("No authentication given.")


        self.logger.debug("Setup namespace")
        masta_datacenter_id = 1 # hardcoded!
        try:
                ip_namespace = self.rpc.callSync(10, "decaf_masta.get_datacenter_ip_namespace", 1)
        except BaseException as e:
                self.logger.error("Error while getting the namespace of datacenter " + str(masta_datacenter_id) + ": \n" + str(e))
                self.logger.error("Falling back to hardcoded namespace.")
                ip_namespace = "qrouter-734784e1-ad3e-4711-ac66-71ddbe9cac02"

        with Namespace("/var/run/netns/%s" % ip_namespace, 'net'):

                pkey_object = paramiko.RSAKey.from_private_key(file_obj=StringIO(privatekey.replace('\\n', '\n')))

                timeout = time.clock() + self.PING_TIMEOUT
                connected = False

                while not connected and time.clock() < timeout:
                    try:
                        self.ssh.connect(hostname=self.host,
                                 username=username,
                                 pkey =pkey_object,
                                 timeout =600,
                                 banner_timeout=600)
                    except BaseException as e:
                        self.logger.error("Error while connecting to the host: %s \n Trying again...\n" % e)
                        time.sleep(3)
                    else:
                        connected = True

                if not connected:
                    raise BaseException("Element manager not connected, not trying again.")

        self.ssh.exec_command("mkdir {path}".format(path=self.TMP_FILE_DIR))

        # Upload interface scripts and other files
        try:
            self.upload_file(get_res(self.CREATE_IFACE_SCRIPT), self.CREATE_IFACE_SCRIPT_REMOTE)
            self.upload_file(get_res(self.CREATE_IFACE_PYTHON), self.CREATE_IFACE_PYTHON_REMOTE)
            self.upload_file(get_res(self.DELETE_IFACE_SCRIPT), self.DELETE_IFACE_SCRIPT_REMOTE)
            self.upload_file(get_res(self.DELETE_IFACE_PYTHON), self.DELETE_IFACE_PYTHON_REMOTE)

            if self.file_urls:
                self.logger.debug("Uploading files")
                for file in self.file_urls:
                    handle = self.download_file(self.files[file])
                    path = "{0}/{1}".format(self.TMP_FILE_DIR, handle.name)
                    self.files[file] = path
                    self.upload_tmp_file(handle, path)
            pass
        except BaseException as e:
            self.logger.error("Error while uploading files to VM: \n %s"%e)
            raise e

        # Don't worry this is generated in any case
        messages = self.after_startup()

        self.logger.debug("Element Manager started: \n")
        self.logger.debug("Received Outputs: \n")
        for output in messages[0]:
            self.logger.debug("Output : %s \n" % output)
        self.logger.debug("Received Errors: \n")
        for error in messages[1]:
            self.logger.debug("Error : %s \n" % error)

        return True

    @Out("Success", bool)
    def stop(self):
        """
        Stops the Element Manager. Deregisters methods and closes the SSH connection.

        :return: True
        """

        for method in self.PERMITTED_METHODS:
            self.rpc.deregister("%s.%s" % (self.instance_id, method))
        self.ssh.close()
        self.instance_desc = None
        self.vm_desc = None
        self.mgmt_interface_desc = None
        self.auth = None
        self.file_urls = None

        return True

    def download_file(self, file_url):

        self.logger.debug("Downloading file from URL %s" % file_url)
        url_handle = url.urlopen(file_url)
        file_name = file_url.split('/')[-1]
        file_handle = open(file_name, 'wb')

        block_sz = 8192
        while True:
            buffer = url_handle.read(block_sz)
            if not buffer:
                break
            file_handle.write(buffer)

        file_handle.close()
        self.logger.debug("Downloading SUCCESS")
        return file_handle

    def upload_file(self, local_dir, remote_dir):
        self.logger.debug("Uploading file to %s" % remote_dir)
        try:
            sftp = self.ssh.open_sftp()

            sftp.put(local_dir, remote_dir)
            sftp.close()
        except BaseException as e:
            self.logger.error("Could not upload %s to %s using SFTP: \n %s" % (local_dir,remote_dir,e))
            raise e
        self.logger.debug("Uploading SUCCESS")

    def upload_tmp_file(self, local_handle, remote_dir):
        self.logger.debug("Uploading file to %s" % remote_dir)
        try:
            sftp = self.ssh.open_sftp()
            sftp.putf(local_handle, remote_dir)
            sftp.close()
        except BaseException as e:
            self.logger.error("Could not upload file to %s using SFTP: \n %s" % (remote_dir,e))
            raise e
        self.logger.debug("Uploading SUCCESS")


    @In("iface_instance_id", unicode)
    @Out("output", tuple)
    def create_interface(self, iface_instance_id):
        """
        Creates an internal interface on a VM.
        Sets up the interface description in /etc/network/interfaces and starts the interface.

        :param iface_instance_id: The interface instance ID registered in Storage.
        :return: A tuple (sys_out, errors) of lists of Strings, containing the System Out output and the errors.
        """

        assert iface_instance_id

        try:
            iface = self.storage.get("interface_instance", options=[], filters={"uuid": iface_instance_id})[0]
        except BaseException as e:
            self.logger.error("Error while fetching interface instance %s from the storage: \n %s" % (iface_instance_id, e))
            return


        kwargs = {
            "iface_instance_id": iface["uuid"],
            "type": iface["type"],
            "internal": iface["internal_name"], # the name of the internal interface (in the specification)
            "external": iface["external_name"], # the name of the external interface (in the specification)
            "iface": iface["physical_name"], # the physical name of the interface
            "internal_or_public": "internal"
        }

        outputs = list()
        errors = list()

        stdin, stdout, stderr = self.ssh.exec_command(self.CREATE_IFACE_COMMAND.format(**kwargs))
        lines = stdout.readlines()
        outputs.append(lines)
        for line in lines:
                self.logger.info(line)
        lines = stderr.readlines()
        errors.append(lines)
        for line in lines:
                self.logger.error(line)
        return outputs, errors



    @In("iface", unicode)
    @Out("output", tuple)
    def delete_interface(self, iface_instance_id=None):
        """
        Deletes an internal interface on a VM.
        Deletes the interface description in /etc/network/interfaces and stops the interface.

        :param iface_instance_id: The interface instance ID registered in Storage.
        :return: A tuple (sys_out, errors) of lists of Strings, containing the System Out output and the errors.
        """

        try:
            iface = self.storage.get("interface_instance", options=[], filters={"uuid": iface_instance_id})[0]
        except BaseException as e:
            self.logger.error("Error while fetching interface instance %s from the storage: \n %s" % (iface_instance_id, e))
            return

        kwargs = {
            "iface_instance_id": iface_instance_id,
            "physical_iface": iface["physical_name"],
        }

        self.logger.debug(json.dumps(kwargs, indent=4))

        outputs = list()
        errors = list()
        self.ssh.exec_command("mkdir {path}".format(path=self.TMP_FILE_DIR))
        stdin, stdout, stderr = self.ssh.exec_command(self.DELETE_IFACE_COMMAND.format(**kwargs))
        lines = stdout.readlines()
        outputs.append(lines)
        for line in lines:
                self.logger.info(line)
        lines = stderr.readlines()
        errors.append(lines)
        for line in lines:
                self.logger.error(line)
        return outputs, errors

    def __generator_wrapper(self, function):

        def call(*args, **kwargs):
            try:
                generator = function(*args, **kwargs)
                outputs = list()
                errors = list()
                for res in generator:
                    command, inputs = res
                    self.logger.info("Executing command '%s' on machine '%s'", command, self.host)
                    stdin, stdout, stderr = self.ssh.exec_command(command, timeout=20)
                    if inputs:
                        for inp in inputs:
                            stdin.write("%s\n"%inp)
                            stdin.flush()
                    lines = stdout.readlines()
                    outputs.append(lines)
                    for line in lines:
                        self.logger.info("Outputs received:")
                        self.logger.info(line)
                    lines = stderr.readlines()
                    errors.append(lines)
                    for line in lines:
                        self.logger.info("Errors received:")
                        self.logger.error(line)
                return outputs, errors
            except BaseException as e:
                self.logger.error("Error while executing %s: \n %s" % (function,e))
                raise e

        return call

    def generate_methods(self, methods):

        assert self.rpc

        def make_dummy(method):

            def dummy(*args, **kwargs):
                self.logger.debug("Method %s is available on this ElementManager. Check the Descriptor file" % method)
                return True

            return dummy

        def make(commands):

            def generator(*args, **kwargs):
                if self.files:
                    kwargs.update(self.files)
                for command in commands:
                    yield command.format(**kwargs), None

            return generator

        for method in methods:
                try:
                    self.logger.error("Generating method: %s" % method)
                    generator = make(methods[method])
                    self.__setattr__(method,self.__generator_wrapper(generator))
                    self.rpc.register("%s.%s" % (self.instance_id, method), self.__getattribute__(method))
                except :
                    self.logger.error("Method %s can't be generated", method)
                    if method in self.PERMITTED_METHODS:
                        self.rpc.register("%s.%s" % (self.instance_id, method), make_dummy(method))

        for method in self.PERMITTED_METHODS:
            if method not in methods:
                self.rpc.register("%s.%s" % (self.instance_id, method), make_dummy(method))
