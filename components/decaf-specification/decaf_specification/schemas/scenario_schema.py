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
#Network scenario descriptor schema. This schema will be considered as the data structure of our network scenario
'''
    class NetworkScenario {
        public string name;
        public string description;
        public Topology topology;
    }
    class Topology {
        public List_of_NodeScenario nodesS;
        public List_of_ConnectionScenario connectionsS;

    }

    class NodeScenario {
        public String nodeName;
        public Enum[VNF, Other_network, ..] type;
        public String nodeModel;

    }
'''
nsd_schema = {
    "title":"network scenario descriptor information schema v0.1",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type":"object",
    "properties":{
        "name":bs.name_schema,
        "description": bs.description_schema,
        "topology":{
            "type":"object",
            "properties":{
                "nodes": {
                    "type":"object",
                    "patternProperties":{
                        ".": {
                            "type": "object",
                            "properties":{
                                "type":{"type":"string", "enum":["VNF", "other_network", "network", "external_network"]}
                            },
                            "patternProperties":{
                                "^(VNF )?model$": {"type": "string"}
                            },
                            "required": ["type"]
                        }
                    }
                },
                "connections": {
                    "type":"object",
                    "properties":{
                        ".": {
                            "type": "object",
                            "properties":{
                                "nodes":{"oneOf":[{"type":"object", "minProperties":2}, {"type":"array", "minLength":2}]}
                            },
                            "required": ["nodes"]
                        },
                        "public_interfaces":  {"type":"array", "minLength": 1 },
                    },
                    "required": ["public_interfaces"],
                }
            },
            "required": ["nodes"],
            "additionalProperties": False
        }
    },
    "required": ["name","topology"],
    "additionalProperties": False
}

scenario_edit_schema = {
    "title":"edit scenario information schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type":"object",
    "properties":{
        "name":bs.name_schema,
        "description": bs.description_schema,
        "topology":{
            "type":"object",
            "properties":{
                "nodes": {
                    "type":"object",
                    "patternProperties":{
                        "^[a-fA-F0-9]{8}(-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$": {
                            "type":"object",
                            "properties":{
                                "graph":{
                                    "type": "object",
                                    "properties":{
                                        "x": bs.integer0_schema,
                                        "y": bs.integer0_schema,
                                        "ifaces":{ "type": "object"}
                                    }
                                },
                                "description": bs.description_schema,
                                "name": bs.name_schema
                            }
                        }
                    }
                }
            },
            "required": ["nodes"],
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}

scenario_action_schema = {
    "title":"scenario action information schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type":"object",
    "properties":{
        "start":{
            "type": "object",
            "properties": {
                "instance_name":bs.name_schema,
                "description":bs.description_schema,
                "datacenter": {"type": "string"}
            },
            "required": ["instance_name"]
        },
        "deploy":{
            "type": "object",
            "properties": {
                "instance_name":bs.name_schema,
                "description":bs.description_schema,
                "datacenter": {"type": "string"}
            },
            "required": ["instance_name"]
        },
        "reserve":{
            "type": "object",
            "properties": {
                "instance_name":bs.name_schema,
                "description":bs.description_schema,
                "datacenter": {"type": "string"}
            },
            "required": ["instance_name"]
        },
        "verify":{
            "type": "object",
            "properties": {
                "instance_name":bs.name_schema,
                "description":bs.description_schema,
                "datacenter": {"type": "string"}
            },
            "required": ["instance_name"]
        }
    },
    "minProperties": 1,
    "maxProperties": 1,
    "additionalProperties": False
}

instance_scenario_action_schema = {
    "title":"instance scenario action information schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type":"object",
    "properties":{
        "start":{"type": "null"},
        "pause":{"type": "null"},
        "resume":{"type": "null"},
        "shutoff":{"type": "null"},
        "shutdown":{"type": "null"},
        "forceOff":{"type": "null"},
        "rebuild":{"type": "null"},
        "reboot":{
            "type": ["object","null"],
        },
        "vnfs":{"type": "array", "items":{"type":"string"}},
        "vms":{"type": "array", "items":{"type":"string"}}
    },
    "minProperties": 1,
    #"maxProperties": 1,
    "additionalProperties": False
}
