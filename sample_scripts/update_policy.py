import json
import argparse
from proofpoint_itm import ITMClient
from proofpoint_itm.classes import AgentPolicy


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--settings", default="settings.json",
                    help="Settings file")
parser.add_argument('--file', '-f', type=str, required=True,
                    help='file name/path for the list of usernames to add to a policy')
parser.add_argument('--policy', '-p', type=str, required=True,
                    help='The name of the policy to update')
args = parser.parse_args()

# read in the config settings and get client
with open(args.settings, 'r') as f:
    settings = json.loads(f.read())

itm_client = ITMClient(settings)

target_policy = itm_client.get_agent_policies(params={'alias': args.policy})
target_policy_id = target_policy[0]['id']
agentpolicy = AgentPolicy(target_policy[0]['policy'])

# import data
with open (args.file, 'r') as f:
    usernames = [u.strip() for u in f]

# build the match condition with username list
match = {
    "simple": {
        "rules": [
            {"user.username": usernames}
        ]
    },
    "modifiers": {
        "evaluation": {
            "unknownFieldsAs": True
        }
    }
}

# update the policy object
agentpolicy.match = match

# push to API
resp = itm_client.overwrite_agent_policy(target_policy_id, agentpolicy)

if resp['_status']['status'] == '200':
    print('Updated AgentPolicy successfully')

try:
    publish_resp = itm_client.publish_config()
except Exception as e:
    # handle exception here, sleep 60 sec, try again, etc
    print(f'Caught exception: {e}')

