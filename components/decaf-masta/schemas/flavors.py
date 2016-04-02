__author__ = 'Kristian Hinnenthal'

#Flavor
flavorschema = {
    "type":"object",
    "properties":{
        "flavor": {
            "type":"object",
            "properties":{
                "flavor_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "ram": {
                    "type": "number"
                },
                "vcpus": {
                    "type": "number"
                },
                "disk": {
                    "type": "number"
                },
                "datacenter_id": {
                    "type": "number"
                },
                "description": {
                    "type": "string"
                }
            },
            "required": ["flavor_id","name","ram","vcpus","disk","datacenter_id","description"],
            "additionalProperties": False
        }
    },
    "required": ["flavor"],
    "additionalProperties": False
}