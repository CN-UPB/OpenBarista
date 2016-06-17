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

    def __init__(self, logger=None, config=None):
        # fake being masta, so we don't have to change other code
        self.__class__.__name__ == "masta"
        super(Pasta, self).__init__(logger=logger, config=config)

        self.logger.info('Checking configuration')

        # Sample format
        # datacenters:
        #   datacenter:
        #     datacenter_id: uint
        #     datacenter_name: string
        #     datacenter_url: url
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
        self.logger.info('Seems sane.')

    def _before_connect(self, url=None, rpc=None, routing_key=None):
        pass

    # same behaviour as masta
    def _after_connect(self):
        self.rpc.set_json_encoder(StorageJSONEncoder)
        self.storage = Endpoint(self.rpc, self.logger)

        # Check if all the datacenters are also registered in Storage, if not, register them

        storage_datacenters = self.storage.get('datacenter', options=[], filters={})

        for datacenter in self.datacenters:
            datacenter_id = datacenter.datacenter_id

            storage_datacenters = self.storage.get('datacenter', options=[],
                                                   filters={"datacenter_masta_id": datacenter.datacenter_id})

            if len(storage_datacenters) == 0:
                # Datacenter not existent, create in Storage

                self.logger.info(
                    "Found datacenter in pasta database that is not registered in decaf_storage. Attempting to register"
                    "it in decaf_storage.")

                self.storage.add('datacenter', data={
                    "name": datacenter.datacenter_name,
                    "description": "Description created by MaSta.",
                    "type": "openstack",
                    "datacenter_masta_id": datacenter.datacenter_id
                })


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

def daemon():
    daemonize(Pasta)

if __name__ == '__main__':
    daemon()
