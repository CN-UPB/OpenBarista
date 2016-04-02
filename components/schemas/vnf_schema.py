__author__ = 'sdjoum'

import basic_schema as bs



internal_connection_element_schema = {
    "type":"object",
    "properties":{
        "VNFC": bs.nameshort_schema,
        "local_iface_name": bs.nameshort_schema
    }
}

internal_connection_schema = {
    "type":"object",
    "properties":{
        "name": bs.name_schema,
        "description":bs.description_schema,
        "type":{"type":"string", "enum":["bridge","data","ptp"]},
        "elements": {"type" : "array", "items": internal_connection_element_schema, "minItems":2}
    },
    "required": ["name", "type", "elements"],
    "additionalProperties": False
}

external_connection_schema = {
    "type":"object",
    "properties":{
        "name": bs.name_schema,
        "type":{"type":"string", "enum":["mgmt","bridge","data"]},
        "VNFC": bs.nameshort_schema,
        "local_iface_name": bs.nameshort_schema ,
        "description":bs.description_schema
    },
    "required": ["name", "type", "VNFC", "local_iface_name"],
    "additionalProperties": False
}

interfaces_schema={
    "type":"array",
    "items":{
        "type":"object",
        "properties":{
            "name":bs.nameshort_schema,
            "dedicated":{"type":"string","enum":["yes","no","yes:sriov"]},
            "bandwidth":bs.bandwidth_schema,
            "vpci":bs.pci_schema,
            "mac_address": bs.mac_schema
        },
        "additionalProperties": False,
        "required": ["name","dedicated", "bandwidth"]
    }
}

bridge_interfaces_schema={
    "type":"array",
    "items":{
        "type":"object",
        "properties":{
            "name": bs.nameshort_schema,
            "bandwidth":bs.bandwidth_schema,
            "vpci":bs.pci_schema,
            "mac_address": bs.mac_schema,
            "model": {"type":"string", "enum":["virtio","e1000","ne2k_pci","pcnet","rtl8139"]}
        },
        "additionalProperties": False,
        "required": ["name"]
    }
}

data_interfaces_schema={
    "type":"array",
    "items":{
        "type":"object",
        "properties":{
            "name": bs.nameshort_schema,
            "bandwidth":bs.bandwidth_schema,
            "vpci":bs.pci_schema,
            "mac_address": bs.mac_schema,
            "model": {"type":"string", "enum":["virtio","e1000","ne2k_pci","pcnet","rtl8139"]}
        },
        "additionalProperties": False,
        "required": ["name"]
    }
}

devices_schema={
    "type":"array",
    "items":{
        "type":"object",
        "properties":{
            "type":{"type":"string", "enum":["disk","cdrom","xml"] },
            "image": bs.path_schema,
            "image metadata": bs.metadata_schema,
            "vpci":bs.pci_schema,
            "xml":bs.xml_text_schema,
        },
        "additionalProperties": False,
        "required": ["type"]
    }
}


numa_schema = {
    "type": "object",
    "properties": {
        "memory":bs.integer1_schema,
        "cores":bs.integer1_schema,
        "paired-threads":bs.integer1_schema,
        "threads":bs.integer1_schema,
        "cores-id":{"type":"array","items":bs.integer0_schema},
        "paired-threads-id":{"type":"array","items":{"type":"array","minItems":2,"maxItems":2,"items":bs.integer0_schema}},
        "threads-id":{"type":"array","items":bs.integer0_schema},
        "interfaces":interfaces_schema
    },
    "additionalProperties": False,
    #"required": ["memory"]
}

vnfc_schema = {
    "type":"object",
    "properties":{
        "name": bs.name_schema,
        "description": bs.description_schema,
        "VNFC image": bs.path_schema,
        "image metadata": bs.metadata_schema,
        "ram":bs.integer0_schema,
        "vcpus":bs.integer0_schema,
        "disk":bs.integer0_schema,
        "data-ifaces": interfaces_schema,
        "bridge-ifaces": bridge_interfaces_schema,
        "devices": devices_schema
    },
    "required": ["name", "VNFC image"],
    "additionalProperties": False
}

vnfd_schema_v01 = {
    "title":"vnfd information schema v0.1",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type":"object",
    "properties":{
        "vnf":{
            "type":"object",
            "properties":{
                "name": bs.name_schema,
                "description": bs.description_schema,
                "class": bs.name_schema,
                "public": {"type" : "boolean"},
                "physical": {"type" : "boolean"},
                "external-connections": {"type" : "array", "items": external_connection_schema, "minItems":1},
                "internal-connections": {"type" : "array", "items": internal_connection_schema, "minItems":1},
                "VNFC":{"type" : "array", "items": vnfc_schema, "minItems":1}
            },
            "required": ["name","external-connections"],
            "additionalProperties": True
        }
    },
    "required": ["vnf"],
    "additionalProperties": False
}

vnfd_schema = {
    "title":"vnfd information schema v0.2",
    "$schema": "http://json-schema.org/draft-04/schema#",
    #"oneOf": [vnfd_schema_v01, vnfd_schema_v02]
    "oneOf": [vnfd_schema_v01]
}