__author__ = 'Kristian Hinnenthal'

#MonitoringRequest
monitoring_request = {
    "type":"object",
    "properties":{
        "monitoring_request": {
            "type":"object",
            "properties":{
                "type": {
                    "type": "string",
                    "enum": ["memory_usage","cpu_util","disk_usage"]
                },
                "scenario_id": {
                    "type": "string"
                },
                "vnf_id": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "type" :"string",
                            "enum": ["all"]
                        }
                    ]
                }
            },
            "required": ["type","scenario_id","vnf_id"],
            "additionalProperties": False
        }
    },
    "required": ["monitoring_request"],
    "additionalProperties": False
}

#MonitoringResponse
monitoring_response = {
    "type": "object",
    "properties": {
        "monitoring_response": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["memory_usage","cpu_util","disk_usage"]
                },
                "scenario_id": {
                    "type": "integer"
                },
                "monitoring_data": {
                    "type": "array",
                    "properties": {
                        "vnf_id": {
                            "type": "string",
                            "oneOf": [
                                {
                                    "type": "string"
                                },
                                {
                                    "type" :"string",
                                    "enum": ["all"]
                                }
                            ]
                        },
                        "values": {
                            "type": "object",
                            "properties": {
                                "current": {
                                    "type": "number"
                                },
                                "total": {
                                    "type": "number"
                                }
                            },
                            "required": ["current","total"],
                            "additionalProperties": False
                        },
                        "required": ["vnf_id","values"],
                        "additionalProperties": False
                    }
                }

            },
            "required": ["type","scenario_id","monitoring_data"],
            "additionalProperties": False
        }
    },
    "required": ["monitoring_response"],
    "additionalProperties": False
}

#MonitoringAlarmRequest
monitoring_alarm_request = {
    "type":"object",
    "properties":{
        "monitoring_alarm_request": {
            "type":"object",
            "properties":{
                "type": {
                    "type": "string",
                    "enum": ["memory_usage","cpu_util","disk_usage"]
                },
                "scenario_id": {
                    "type": "string"
                },
                "vnf_id": {
                    "type": "string"
                },
                "comparison_operator": {
                    "type": "string",
                    "enum": ["ge","le","eq"]
                },
                "threshold": {
                    "type": "number"
                },
                "threshold_type": {
                    "type": "string",
                    "enum": ["relative","absolute"]
                },
                "statistic": {
                    "type": "string",
                    "enum": ["max","min","avg"]
                }
            },
            "required": ["type","scenario_id","vnf_id","comparison_operator","threshold","threshold_type","statistic"],
            "additionalProperties": False
        }
    },
    "required": ["monitoring_alarm_request"],
    "additionalProperties": False
}