__author__ = 'Kristian Hinnenthal'

#Image
imageschema = {
    "type":"object",
    "properties":{
        "image": {
            "type":"object",
            "properties":{
                "image_id": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "datacenter_id": {
                    "type": "number"
                },
                "description": {
                    "type": "string"
                }
            },
            "required": ["image_id","name","url","datacenter_id","description"],
            "additionalProperties": False
        }
    },
    "required": ["image"],
    "additionalProperties": False
}