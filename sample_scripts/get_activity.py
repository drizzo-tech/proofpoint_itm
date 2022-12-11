import json
import argparse
import os
import pandas as pd
from proofpoint_itm import ITMClient

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--settings", default="settings.json", help="Settings file")
parser.add_argument("-q", "--query", required=True, help="Query file (json format)")
parser.add_argument("-o", "--outfile", help="Output file name/path")
args = parser.parse_args()

with open(args.settings, 'r') as f:
    settings = json.loads(f.read())

itm_client = ITMClient(settings)


# In this example, the query file is the query json exported from that UAM console
# after running an exploration
with open(args.query, 'r') as f:
    query = json.loads(f.read())

events = itm_client.activity_search(query, 'event')

if len(events['data']) > 0:
    if args.outfile:
        fname, fext = os.path.splitext(args.outfile)
        if fext == '.csv':
            df = pd.DataFrame.from_dict(events['data'])
            df.to_csv(args.outfile, index=False, header=True)
        else:
            with open(args.outfile, 'w') as out:
                out.write(json.dumps(events['data'], indent=4))
    else:
        print(json.dumps(events['data'], indent=4))
else:
    print('No events returned from activity search')
