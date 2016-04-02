import sys
import requests
import json

def trigger_alarm(url, alarm_id, value):
    data = {
        "alarm_id": alarm_id,
        "reason_data": {
            "most_recent": value
        }
    }

    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

if __name__ == '__main__':

    url = "http://fg-cn-decaf-head1.cs.upb.de:5001/alarm"

    alarm_id = sys.argv[1]
    value = sys.argv[2]

    trigger_alarm(url, alarm_id, value)