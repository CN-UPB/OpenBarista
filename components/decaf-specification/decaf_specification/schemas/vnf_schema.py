__author__ = 'sdjoum'
# Copyright 2016 DECaF Project Group
# This file is part of the DECaF project and originally derives from OpenMANO
#
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
        "required": ["name", "bandwidth"]
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

auth_schema = {
    "type":"object",
    "properties":{
        "username": bs.name_schema,
        "password": bs.password_schema
    },
    "required": ["username", "password"],
    "additionalProperties": False
}

files_schema = bs.file_schema

event_schema = {
    "type":"object",
    "properties":{
        "after_startup": {"type" : "array", "items": bs.command_schema, "minItems":1},
        "new_successor": {"type" : "array", "items": bs.command_schema, "minItems":1},
        "new_predecessor": {"type" : "array", "items": bs.command_schema, "minItems":1},
        "before_shutdown": {"type" : "array", "items": bs.command_schema, "minItems":1},
    },
    "additionalProperties": True
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
        "VNFC image": bs.http_schema,
        "image metadata": bs.metadata_schema,
        "ram":bs.integer0_schema,
        "vcpus":bs.integer0_schema,
        "disk":bs.integer0_schema,
        "data-ifaces": interfaces_schema,
        "bridge-ifaces": interfaces_schema,
        "max_instance": bs.integer0_schema,
        "auth": auth_schema,
        "events": event_schema,
        "files" : files_schema
    },
    "additionalProperties": True
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
                "VNFC":{"type" : "array", "items": vnfc_schema, "minItems":1},
                "max_instance": bs.integer0_schema
            },
            "required": ["name","external-connections"],
            "additionalProperties": True
        }
    },
    "required": ["vnf"],
    "additionalProperties": True
}

vnfd_schema = {
    "title":"vnfd information schema v0.2",
    "$schema": "http://json-schema.org/draft-04/schema#",
    #"oneOf": [vnfd_schema_v01, vnfd_schema_v02]
    "oneOf": [vnfd_schema_v01]
}