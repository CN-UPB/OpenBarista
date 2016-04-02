#!/usr/bin/env python
__author__ = 'tarun'

import json
import logging
from decaf_storage.json_base import StorageJSONEncoder
from decaf_storage.database import Database
from decaf_storage.storage import Storage

from decaf_storage.model.datacenter import Datacenter



LOGFILE = '/var/log/decaf/loaddata.log'

#class TestStorageAPI(unittest.TestCase):
class TestStorageAPI():

    def __init__(self):
        db = Database({
            "type": 'postgresql',
            #"host": 'fg-cn-decaf-head1.cs.upb.de',
            "host": '127.0.0.1',
            "port": '5432',
            "database": 'decaf_storage',
            "user": 'pgdecaf',
            "password": 'pgdecafpw'
        })
        #db.drop_all()
        #db.init_db()
        # Configure logging
        log_file = LOGFILE
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_file)
        logger.addHandler(fh)

        self.storage = Storage(db, logger=logger)

    def test_scenario_insert(self):
        # add datacenter
        code, dc = self.storage.add(Datacenter, {
            'name': 'name',
            'description': 'description',
            'type': 'openstack',
            'datacenter_masta_id': 1
        })
        print('DC: ', dc)

if __name__ == '__main__':
    test=TestStorageAPI()
    test.test_scenario_insert()
