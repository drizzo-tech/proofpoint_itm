import csv
import json
from proofpoint_itm import ITMClient

# read in the config settings
with open('./dev/settings.json', 'r') as f:
    settings = json.loads(f.read())


itm_client = ITMClient(settings)

instances = itm_client.get_endpoints()


fields = {
"id": "component.id",
"hostname": "endpoint.hostname",
"type": "component.kind",
"realm": "component.realm",
"region": "component.region",
"status": "component.status.code",
"version": "component.version",
"os.type": "endpoint.os.kind",
"os.name": "endpoint.os.name",
"os.version": "endpoint.os.version",
"time": "event.observedAt"
}

def get_value(obj, path):
    keys = path.split(".")
    key = keys.pop(0)
    if key in obj:
        if len(keys) == 0:
            return obj[key]
        else:
            return get_value(obj[key], ".".join(keys))
    else:
        return ""

if len(instances) > 0:
   with open('endpoints.csv', 'w', newline='', encoding='utf-8') as csvfile:
       csvwriter = csv.writer(csvfile)
       csvwriter.writerow([field for field in fields.keys()])
       for instance in instances:
           csvwriter.writerow([
                get_value(instance, fields[field]) for field in fields.keys()
           ])

