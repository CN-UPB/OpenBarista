keystone_creds = {
    "keystone_credentials" : {
        "keystone_url" : "http://controller:5000/v3",
        "keystone_domain_id": "default",
        "keystone_domain_name": "Default",
        "keystone_project_name": "admin",
        "keystone_user" : "demo",
        "keystone_pass" : "FzFOFiMBgUJ6fw"
    }
}

datacenter = {
    "datacenter" : {
        "datacenter_name" : "myDatacenter",
        "keystone_id" : 1,
        "keystone_region" : "RegionOne"
    }
}

datacenter_config = {
    "datacenter_config" : {
        "datacenter_id" : 1,
        "router" : {
            "name": "router"
        },
        "networks": {
            "management_network": {
                "net_name": "management",
                "subnet_name": "management",
                "cidr": "172.16.2.0/24",
                "ip_version": 4,
                "dns_nameserver": "8.8.4.4",
                "gateway": "172.16.2.1"
            },
            "public_network": {
                "net_name": "public",
                "subnet_name": "public",
                "cidr": "192.167.0.0/16",
                "ip_version": 4,
                "allocation_pool": {
                    "start": "192.167.100.0",
                    "end": "192.167.200.0"
                },
                "dns_nameserver": "8.8.4.4",
                "gateway": "192.167.0.1"
            }
        }
    }
}

flavor_data = {
    "flavor": {
        "flavor_id": "test-flavor",
        "name": "CoolFlavor",
        "ram": 512,
        "vcpus": 2,
        "disk": 10,
        "datacenter_id": 1,
        "description": "It is a really cool flavor."
    }
}

flavor_data_test = {
    "flavor": {
        "flavor_id": "test-flavor-id",
        "name": "Test-Flavor",
        "ram": 512,
        "vcpus": 1,
        "disk": 0,
        "datacenter_id": 1,
        "description": "Flavor of our test scenario."
    }
}

image_data = {
    "image": {
        "image_id": "test-image-id",
        "name": "CoolMastaImage",
        "url": "http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img",
        "container_format": "bare", # optional
        "disk_format": "qcow2", # optional
        "datacenter_id": 1,
        "description": "Nice little image."
    }
}

image_webserver_test = {
    "image": {
        "image_id": "webserver-test-image-id",
        "name": "webserver-VM",
        "url": "http://pg:decaf@groups.uni-paderborn.de/decaf/images/simplewebserver.qcow2",
        "datacenter_id": 1,
        "description": "Virtual machine containing webserver image"
    }
}


# A sample deploy graph. The commented attributes are the ones that are added by masta before the graphs is given back as result.
deploy_graph = {
    "graph": {
        "scenario_instance_id": "CoolScenario",

        "nodes": [
            {
                "vm_instance_id": "vnf_1",
                "name": "Testname",
                "metadata": {
                    "datacenter": 1,
                    "image": "TestImage",
                    "flavor": "TestFlavor",
                    "mgmt": "eth0",
                    #"mgmt_physical": "eth0",
                    #"mgmt_ip:" "192.170.0.1",
                    #"keypair": {
                    #    "keypair_id": 1,
                    #    "private_key": "blabla",
                    #    "public_key": "blabla",
                    #    "fingerprint": "blub"
                    #}
                }
            },
            {
                "vm_instance_id": "vnf_2",
                "metadata": {
                    "datacenter": 1,
                    "image": "TestImage",
                    "flavor": "TestFlavor",
                    "mgmt": "eth0",
                    #"mgmt_physical": "eth0",
                    #"mgmt_ip:" "192.170.0.2"
                }
            }
        ],

        "edges": [
            {
                "source": "vnf_1",
                "type": "data",
                "target": "vnf_2",
                "metadata": {
                    "source_internal": "xe0",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid1",
                    #"source_port_physical": "eth1",
                    #"source_port_ip": "10.0.0.10",
                    "target_internal": "xe0",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid2",
                    #"target_port_physical": "eth1",
                    #"target_port_ip": "10.0.0.11",
                }
            },
            {
                "source": "vnf_1",
                "type": "data",
                "target": "vnf_2",
                "metadata": {
                    "source_internal": "xe0",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid3",
                    #"source_port_physical": "eth2",
                    #"source_port_ip:" "10.0.1.10",
                    "target_internal": "xe0",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid4",
                    #"target_port_physical": "eth1",
                    #"target_port_ip:" "10.0.1.11",
                }
            }
        ],

        "public_ports": [
            {
                "vm_instance_id": "vnf_1",
                "type": "data",
                "metadata": {
                    "internal": "xe1", # internal name
                    "external": "data",
                    "interface_instance_id": "uuid5"
                    #"port_physical": "eth2",
                    #"port_ip": "192.168.0.3"
                }
            }
        ]
    }
}

bigger_deploy_graph = {
    "graph": {
        "scenario_instance_id": "aa22c1d7-7dff-4d4f-96bc-2c0ed3c3feda",

        "nodes": [
            {
                "vm_instance_id": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "name": "Firewall",
                "metadata": {
                    "datacenter": 1,
                    "image": "c403907b-42e6-4f05-8575-8699921329d2",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            },
            {
                "vm_instance_id": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "name": "Loadbalancer",
                "metadata": {
                    "datacenter": 1,
                    "image": "f84035d7-cce7-4232-afda-3960d8102b57",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            },
            {
                "vm_instance_id": "3332c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "name": "Webserver",
                "metadata": {
                    "datacenter": 1,
                    "image": "d45e6494-f36a-4c9e-9752-dfb9bbd43e81",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            }
        ],

        "edges": [
            {
                "source": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data",
                "target": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "metadata": {
                    "source_internal": "xe0",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid1",
                    "target_internal": "xe1",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid2",
                }
            },
            {
                "source": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data",
                "target": "3332c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "metadata": {
                    "source_internal": "xe0",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid3",
                    "target_internal": "xe1",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid4",
                }
            }
        ],
        "public_ports": [
            {
                "vm_instance_id": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data1",
                "metadata": {
                    "internal": "xe2",
                    "external": "bla",
                    "interface_instance_id": "uuid13"
                }
            }
        ]
    }
}

small_deploy_graph = {
    "graph": {
        "scenario_instance_id": "ff32c1d7-77ff-4d4f-96bc-2c0ed3c3feda",

        "nodes": [
            {
                "vm_instance_id": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "metadata": {
                    "datacenter": 1,
                    "image": "test-image-id",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            },
            {
                "vm_instance_id": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "metadata": {
                    "datacenter": 1,
                    "image": "test-image-id",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            }
        ],

        "edges": [
            {
                "source": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data",
                "target": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "metadata": {
                    "source_internal": "xe0",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid1",
                    "target_internal": "xe1",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid2",
                }
            }
        ],

        "public_ports": [
            {
                "vm_instance_id": "1232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data1",
                "metadata": {
                    "internal": "xe2",
                    "external": "bla",
                    "interface_instance_id": "uuid13"
                }
            }
        ]
    }
}

one_node_scenario = {
    "graph": {
        "scenario_instance_id": "OneNodeScenario",

        "nodes": [
            {
                "vm_instance_id": "firewall-test-id",
                "name": "Firewall-Test",
                "metadata": {
                    "datacenter": 1,
                    "image": "7b46553a63914f3d868a1a4b013f7544",
                    "flavor": "test-flavor-id",
                    "mgmt": "mgmt",
                }
            }
        ],

        "edges": [
        ],

        "public_ports": [
            {
                "vm_instance_id": "firewall-test-id",
                "type": "data",
                "metadata": {
                    "internal": "int1",
                    "external": "public",
                    "interface_instance_id": "uuid1"
                }
            }
        ]
    }
}

small_add_graph = {
    "graph": {
        "scenario_instance_id": "aa22c1d7-7dff-4d4f-96bc-2c0ed3c3feda",

        "nodes": [
            {
                "vm_instance_id": "ba22c1d7-abc4-4d4f-96bc-2c0e13c3feda",
                "name": "Webserver-2",
                "metadata": {
                    "datacenter": 1,
                    "image": "d45e6494-f36a-4c9e-9752-dfb9bbd43e81",
                    "flavor": "4232c1d7-77ff-4d4f-96bc-2c0ed3c3fed2",
                    "mgmt": "eth0",
                }
            }
        ],
        "edges": [
            {
                "source": "2232c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
                "type": "data",
                "target": "ba22c1d7-abc4-4d4f-96bc-2c0e13c3feda",
                "metadata": {
                    "source_internal": "xe3",
                    "source_external": "bla",
                    "source_interface_instance_id": "uuid10",
                    "target_internal": "xe3",
                    "target_external": "bla",
                    "target_interface_instance_id": "uuid11",
                }
            }
        ],
        "public_ports": [
        ]
    }
}

small_shrink_graph = {
    "graph": {
        "scenario_instance_id": "SmallScenario",

        "nodes": [
            {
                "vm_instance_id": "vnf_1"
            }
        ],
        "edges": [
        ]
    }
}

graph_to_add = {
    "graph": {
        "scenario_instance_id" : "CoolScenario",

        "nodes": [
            {
                "vm_instance_id": "vnf_3",
                "metadata": {
                    "datacenter": 1,
                    "image": "TestImage",
                    "flavor": "TestFlavor",
                    "mgmt": "eth0",
                    #"mgmt_physical": "eth0",
                    #"mgmt_ip:" "192.170.0.3"
                }
            }
        ],

        "edges": [
            {
                "external": False,
                "source": "vnf_1",
                "relation": "data",
                "target": "vnf_3",
                "metadata": {
                    "source_port": "xe3",
                    #"source_port_physical": "eth3",
                    #"source_port_ip:" "10.0.2.10",
                    "target_port": "xe3",
                    #"target_port_physical": "eth3",
                    #"target_port_ip:" "10.0.2.11",
                }
            }
        ]
    }
}

shrink_graph = {
    "graph": {
        "scenario_instance_id" : "9a0ec82833be4aada028cb9cb15eef9d",

        "edges": [
            {
                "metadata": {
                    "source_interface_instance_id": "uuid8",
                    "target_interface_instance_id": "uuid9"
                }
            }
        ]
    }
}

# memory_usage, cpu_util

monitoring_data = {
    "monitoring_request": {
        "type": "memory_usage",
        "vm_instance_id": "3332c1d7-77ff-4d4f-96bc-2c0ed3c3feda"
    }
}

monitoring_alarm_request = {
    "monitoring_alarm_request": {
        "type": "cpu_util", # cpu_util
        "vm_instance_id": "3332c1d7-77ff-4d4f-96bc-2c0ed3c3feda",
        "comparison_operator": "ge",
        "threshold": 0.5,
        "threshold_type": "relative",  # absolute
        "statistic": "max",  # min, avg
        "period": 60 # in seconds
    }
}

monitoring_alarm_event = {
    "monitoring_alarm_event": {
        "subscription_name": "blablabla",
        "value": 100,  # absolute!
        "vm_instance_id": id,
        "monitoring_alarm_request": monitoring_alarm_request["monitoring_alarm_request"]
    }
}

vm_action = {
    "vm_action": {
        "vm_instance_id": "webserver-2-id",
        "action": "pause" # start, stop, soft-reboot, hard-reboot, pause, unpause, suspend, resume, shelve, unshelve
    }
}

scenario_action = {
    "scenario_action": {
        "scenario_instance_id": "blabla",
        "action": "pause" # start, stop, soft-reboot, hard-reboot, pause, unpause, suspend, resume, shelve, unshelve
    }
}
