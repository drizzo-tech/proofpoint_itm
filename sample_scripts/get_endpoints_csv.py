import csv
import json
from proofpoint_itm import ITMClient

# read in the config settings
with open('settings.json', 'r') as f:
    settings = json.loads(f.read())


itm_client = ITMClient(settings)

attrs = '*'
instances = itm_client.get_endpoints(includes=attrs)


if len(instances) > 0:
   with open('endpoints.csv', 'w', newline='', encoding='utf-8') as csvfile:
       csvwriter = csv.DictWriter(csvfile, fieldnames=instances[0].keys())
       csvwriter.writeheader()
       for instance in instances:
           csvwriter.writerow(instance)

