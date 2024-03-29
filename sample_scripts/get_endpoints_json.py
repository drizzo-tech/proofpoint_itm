import csv
import json
from proofpoint_itm import ITMClient


# need to get all enpoints using the registry api / instances
# call with limit=100
# get first page, capture total
# add endpoint data to list
# call again with offset iteration (offset=100, etc)
# add endpoint data to list
# loop to total
# Fields to grab: hostname, updatedAt


# read in the config settings
with open('settings.json', 'r') as f:
    settings = json.loads(f.read())


itm_client = ITMClient(settings)

attrs = '*'
instances = itm_client.get_endpoints(includes=attrs)

try:
    print(json.dumps(instances, indent=4))
except Exception as e:
    print(f'Error: {e}')


