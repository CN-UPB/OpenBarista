__author__ = 'sdjoum'

#Basis schemas
nameshort_schema={"type" : "string", "minLength":1, "maxLength":24, "pattern" : "^[^,;()'\"]+$"}
name_schema={"type" : "string", "minLength":1, "maxLength":36, "pattern" : "^[^,;()'\"]+$"}
xml_text_schema={"type" : "string", "minLength":1, "maxLength":1000, "pattern" : "^[^']+$"}
description_schema={"type" : ["string","null"], "maxLength":200, "pattern" : "^[^'\"]+$"}
id_schema_fake = {"type" : "string", "minLength":2, "maxLength":36 }  #"pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
id_schema = {"type" : "string", "pattern": "^[a-fA-F0-9]{8}(-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$"}
pci_schema={"type":"string", "pattern":"^[0-9a-fA-F]{4}(:[0-9a-fA-F]{2}){2}\.[0-9a-fA-F]$"}
http_schema={"type":"string", "pattern":"^https?://[^'\"=]+$"}
bandwidth_schema={"type":"string", "pattern" : "^[0-9]+ *([MG]bps)?$"}
memory_schema={"type":"string", "pattern" : "^[0-9]+ *([MG]i?[Bb])?$"}
integer0_schema={"type":"integer","minimum":0}
integer1_schema={"type":"integer","minimum":1}
path_schema={"type":"string", "pattern":"^(\.(\.?))?(/[^/"":{}\ \(\)]+)+$"}
vlan_schema={"type":"integer","minimum":1,"maximum":4095}
vlan1000_schema={"type":"integer","minimum":1000,"maximum":4095}
mac_schema={"type":"string", "pattern":"^[0-9a-fA-F][02468aceACE](:[0-9a-fA-F]{2}){5}$"}  #must be unicast LSB bit of MSB byte ==0
url_schema={"type":"string", "pattern" : "^(http|ftps|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?$"}
queue_schema={"type":"string", "minLength":1}
#mac_schema={"type":"string", "pattern":"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"}
ip_schema={"type":"string","pattern":"^([0-9]{1,3}.){3}[0-9]{1,3}$"}
port_schema={"type":"integer","minimum":1,"maximum":65534}
metadata_schema={
    "type":"object",
    "properties":{
        "architecture": {"type":"string"},
        "use_incremental": {"type":"string","enum":["yes","no"]},
        "vpci": pci_schema,
        "os_distro": {"type":"string"},
        "os_type": {"type":"string"},
        "os_version": {"type":"string"},
        "bus": {"type":"string"}
    }
}
