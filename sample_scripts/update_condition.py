from proofpoint_itm import ITMClient
from proofpoint_itm.classes import Predicate
import json
import argparse

# need to update a condition/list via depot api
# need to have a predicate alias
# search depot for the predicate alias
# capture the "definition" and "patterns" fields
# add username to "definition" > "$and" > "$stringIn" > "user.name" list
# add key/value for username in patterns list  { "key": "user.name", "value": username }

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--settings", default="settings.json", help="Settings file")
parser.add_argument("-f", "--file", help="File containing condition list items")
parser.add_argument("--alias", help="Alias id of the Condition/List to update")
parser.add_argument("--attr", help="Attribute name used for condition values")
parser.add_argument("-m", "--match", help="Match type for condition values")
parser.add_argument("-p", "--prefix", help="Prefix to add to each condition value")
args = parser.parse_args()


# read in the config settings and get client
with open(args.settings, 'r') as f:
    settings = json.loads(f.read())

itm_client = ITMClient(settings)

query = {
    "query": {
        "bool": {
            "filter": {
                "term": {
                    "alias": args.alias
                }
            }
        }
    }
}

target_predicate = itm_client.depot_search(query, entity='predicate')
predicate = Predicate(target_predicate[0])

# build new condition definition
condition_list = []
with open(args.file, 'r') as fh:
    for line in fh:
        line = line.strip()
        if args.prefix:
            condition_list.append(args.prefix + line)
        else:
            condition_list.append(line)

definition = {'$and': [{f'${args.match}': {args.attr: condition_list}}]}

patterns = []
for entry in condition_list:
    pattern = {'key': args.attr, 'value': entry}
    patterns.append(pattern)

predicate.definition = definition
predicate.patterns = patterns

resp = itm_client.update_predicate(target_predicate[0]['id'], predicate)

if resp['_status']['status'] == '200':
    print('Condition successfully updated')

try:
    publish_resp = itm_client.publish_config()
except Exception as e:
    # handle exception here, sleep 60 sec, try again, etc
    print(f'Caught exception: {e}')