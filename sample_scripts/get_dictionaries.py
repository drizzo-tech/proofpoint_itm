import csv
import json
from proofpoint_itm import ITMClient


# read in the config settings
with open('settings.json', 'r') as f:
    settings = json.loads(f.read())

itm_client = ITMClient(
    settings['ITM']['base_url'],
    settings['ITM']['client_id'],
    client_secret=settings['ITM']['client_secret'])

# get list of all dictionaries
dictionaries = itm_client.get_dictionaries()
print(dictionaries['data'])

# get a specific dictionary by ID
dict_id = 'Dictionary-disease_keywords'
dictionary = itm_client.get_dictionary(dict_id)
print(dictionary)

# updating an existing dictionary requires list of dict objects
# for each keyword
kw_list = {
    "entries": [
        {
            "term": "keyword1",
            "type": "CaseInsensitive",
            "weight": 1,
            "count": 1
        },
        {
            "term": "keyword2",
            "type": "CaseInsensitive",
            "weight": 1,
            "count": 1
        }
    ]
}

result = itm_client.update_dictionary(dict_id, kw_list)

print('stop here')