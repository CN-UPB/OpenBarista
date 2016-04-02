import json

import requests

from decaf_masta import masta

controller = masta.MastaController()

try:
    
    datacenter_data = { "datacenter" : {
        "datacenter_name" : "myDatacenter",
        "keystone_url" : "http://192.168.0.15:5000/v2.0",
        "keystone_tenant" : "service",
        "keystone_user" : "decaf-masta",
        "keystone_pass" : "masta2991874"
        }
    }

    #controller.add_datacenter(json.dumps(datacenter_data))
    
    #print(controller.get_datacenters())
    #print(controller.get_keystone_credentials(1))
    
    #print(controller.get_datacenter_stats(1))

    #controller.masta_agent.get_vm_info()
    #instance_data = {"name":"sampleMasta","flavorId":"1","imageId":"e5601e05-9702-4e49-a4fc-129e26a2cbcc"}
    #instance_id = controller.masta_agent.new_vminstance(json.dumps(instance_data))
    #print(instance_id)

    #print(controller.masta_agent.delete_vminstance("3acaf224-71a4-4246-8d37-d3c6b3b09934"))

    #print(controller.masta_agent.action_vminstance("ee9a162c-cd0e-4d88-b880-3a35ec6b1391",structs.InstanceAction.resume))

    #print(controller.masta_agent.new_image("testImageXY","/home/pgdecaf/Downloads/cirros-0.3.4-x86_64-disk.img"))
    
    #print(controller.masta_agent.delete_image("ecac1bca-6cef-46fe-b3dd-8c35b1128edd"))

    flavor_data = {"flavor": {"name": "masta_super_flavor","ram": 1024,"vcpus": 2,"disk": 10}}
    print(controller.new_flavor(json.dumps(flavor_data)))

    #print(controller.masta_agent.delete_flavor("10"))

    #controller.set_event_handler(test_function)
    
    controller.disconnect()

    pass

except (BaseException) as error:
    print(error)
