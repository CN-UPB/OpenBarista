import logging

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

controller = MastaController(db, logger, None)

# ---------------------------------------------------

#print(controller.add_keystone_credentials(json.dumps(ex.keystone_creds)))
#print(controller.get_keystone_credentials(2))
#print(controller.get_keystones())
#print(controller.add_datacenter(json.dumps(ex.datacenter)))

print(controller.destroy_scenario("SmallScenario"))
#print(controller.deploy_scenario(ex.small_deploy_graph))
#print(controller.extend_scenario(ex.small_add_graph))
#print(controller.shrink_scenario(ex.small_shrink_graph))
#print(controller.new_flavor(ex.flavor_data_test))
#print(controller.new_image(ex.image_data_test))
#print(controller.destroy_scenario("CoolScenario"))
#print(controller.get_monitoring_data(json.dumps(ex.monitoring_data)))
#print(controller.create_monitoring_alarm(json.dumps(ex.monitoring_alarm_request)))
#print(controller.delete_monitoring_alarm("masta.alarm.2"))
#print(controller.get_vm_ip("418c60e2945141fca91d3a61bda1e147","name-name"))
#print(controller.masta_agents[1].new_keypair("test"))
#print(controller.masta_agents[1].delete_keypair("test"))
#print(controller.masta_agents[1].list_ports("86a38d6b-8cdf-4594-9d58-02c9e70b5dee"))