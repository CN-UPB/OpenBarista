import json
import logging

import tests.example_datatypes as ex
from decaf_masta.components.database.mastadatabase import Database
from decaf_masta.masta import MastaController

db_data = {
    "type" : "mysql",
    "host" : "fg-cn-sandman1.cs.upb.de",
    "port" : 3306,
    "database": "masta_db",
    "user": "masta",
    "password": "masta811729"
}

db = Database(db_data)
db.init_db()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

controller = MastaController(db,logger)

controller.deploy_scenario(json.dumps(ex.deploy_graph))

#controller.destroy_scenario("jaskdh")

#controller.action_scenario("jaskdh",structs.ScenarioAction.resume)

#controller.add_nodes(json.dumps(ex.nodes_to_add))

#controller.delete_nodes(["vnf1.vm2@1#1"])