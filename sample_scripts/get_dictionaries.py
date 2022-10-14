import json
import argparse
from proofpoint_itm import ITMClient
from proofpoint_itm.classes import Dictionary


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--settings", default="settings.json", help="Settings file")
parser.add_argument("-q", "--query", required=True, help="Query file (json format)")
parser.add_argument("-o", "--outfile", help="Output file name/path")
args = parser.parse_args()

with open(args.settings, 'r') as f:
    settings = json.loads(f.read())

itm_client = ITMClient(settings)

# get list of all dictionaries
dictionaries = itm_client.get_dictionaries()
print(dictionaries['data'])

# get a specific dictionary by ID
dict_id = 'Dictionary-disease_keywords'
dictionary = Dictionary({'name': dict_id, 'description': 'Disease Keywords'})
print(dictionary.as_dict())

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

dictionary.entries = kw_list['entries']

result = itm_client.update_dictionary(dictionary)

print('stop here')