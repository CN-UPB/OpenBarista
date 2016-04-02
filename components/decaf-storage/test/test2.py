#!/usr/bin/env python
import json
import logging
import unittest

from database import Database
from decaf_storage.json_base import StorageJSONEncoder
from storage import Storage


class TestStorageAPI(unittest.TestCase):

    def setUp(self):

        db = Database({
            "type": 'postgresql',
            "host": 'localhost',
            "port": '5432',
            "database": 'decaf_storage',
            "user": 'decaf',
            "password": 'decafpw'
        })
        # db.drop_all()
        db.init_db()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.engine').addHandler(ch)
        self.storage = Storage(db, logger=logger)

    def test_scenario_insert(self):
        for vnf in self.storage.get_vnf(
                filters={'uuid': '7061c9d3fd7748d1845781c8979cc2f5'},
                options=['vms', 'scenario_vnfs.scenario']):
            print(json.dumps(vnf, cls=StorageJSONEncoder, check_circular=True))

if __name__ == '__main__':
    unittest.main()
