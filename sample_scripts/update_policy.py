import json
import argparse
from proofpoint_itm import ITMClient
import pdb



parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', type=str, required=True,
                    help='file name/path for the list of usernames to add to a policy')
parser.add_argument('--policy', '-p', type=str, required=True,
                    help='The name of the policy to update')
parser.add_argument('--action', '-a', choices=['update', 'overwrite'], default='update',
                    help='Choose update or overwrite action, defaults to update')
args = parser.parse_args()

# read in the config settings
with open('settings.json', 'r') as f:
    settings = json.loads(f.read())


itm_client = ITMClient(
    settings['ITM']['base_url'],
    settings['ITM']['client_id'],
    client_secret=settings['ITM']['client_secret'])

policy = itm_client.get_policies(params={'alias': args.policy})
policy_id = policy['data'][0]['id']

# import data
with open (args.file, 'r') as f:
    usernames = [u.strip() for u in f]

pdb.set_trace()
if args.action == 'update':
    # build web request body
    data = {
        'match': {
            'simple': {
                'rules': [
                    {
                        'user.username': usernames
                    }
                ]
            }
        }
    }

    # update policy
    policy_update = itm_client.update_policy(policy_id, data)
    if policy_update['_status']['status'] != 200:
        err_msg = policy_update['_status']['status']
        print(f'Error during policy update: {err_msg}')

elif args.action == 'overwrite':
    policy['data'][0]['policy']['match']['simple']['rules'][0]['user.username'] = usernames
    
    policy_update = itm_client.overwrite_policy(policy_id, policy['data'][0])
    if policy_update['_status']['status'] != 200:
        msg = policy_update['_status']['message']
        detail = policy_update['_status']['params']['details'][0]['message']
        err_msg = f'{msg}: {detail}'
        print(f'{err_msg}')

