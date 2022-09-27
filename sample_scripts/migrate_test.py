import enum
import json
import argparse
import os
import logging
from proofpoint_itm import ITMClient
from proofpoint_itm.classes import Predicate, Rule, Tag, Policy, Target, TargetGroup


import pdb

pdb.set_trace()

# TODO: For future versions/features
# get a target tenant client
# grab the target tenant ID
# Better logging
# MIP Classification Accounts
# MIP Labels

update_agent_policies = ['242adc7f-242c-4925-9bab-305463cfae21']

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', required=False, help='Source tenant settings file')
parser.add_argument('-t', '--target', required=False, help='Target tenant settings file')
parser.add_argument('--test', action='store_true', default=False, help='Test mode, no changes written')
args = parser.parse_args()

logging.basicConfig(
    filename='migration.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
    )
logging.info('Migration script starting\n\n')

with open(args.source, 'r') as f:
    source_settings = json.loads(f.read())

# with open(args.source, 'r') as f:
#     target_settings = json.loads(f.read())

s_client = ITMClient(source_settings)



# get notification policies (target-groups)
notify_policy_map = {}
logging.info('----- Creating notification policies: -----')
s_target_groups = s_client.get_notification_policies()
for s_target_group in s_target_groups:
    
    if s_target_group['status'] == 'deleted':
        continue

    # fix up the targets (remove id)
    targets = []
    for s_target in s_target_group['targets']:
        target = Target(s_target)
        targets.append(target.__dict__)

    target_group = TargetGroup(s_target_group)
    target_group.targets = targets
    res = s_client.create_notification_policy(target_group, test=True)
    notify_policy_map[s_target_group['id']] = res['id']
    logging.info(json.dumps(target_group.__dict__))
logging.info('----- Notification policies complete -----\n')

    

# get tags
tag_map = {}
tag_tracker = []
s_tags = s_client.get_tags()
logging.info('----- Creating tags: -----')
for s_tag in s_tags:
    # skip public tags, but keep mapping for later
    if s_tag['extent'] == 'public':
        tag_map[s_tag['id']] = s_tag['id']
        continue

    # API seems to return duplicate tags, dealing with that
    if s_tag['id'] not in tag_tracker:
        tag_tracker.append(s_tag['id'])
        tag = Tag(s_tag)

        res = s_client.create_tag(tag, test=True)
        tag_map[s_tag['id']] = res['id']
        logging.info(json.dumps(tag.__dict__))
logging.info('----- Tags complete -----\n')

# get predicates
predicate_map = {}
predicate_cache = {}
saved_predicates = []
logging.info('----- Updating predicates: ------')
s_predicates = s_client.get_predicates()
for s_predicate in s_predicates:
    
    # skip built-in predicates
    if s_predicate['extent'] == 'public':
        predicate[s_predicate['id']] = s_predicate['id']
        continue

    # predictes that ref other predicates will wait
    if s_predicate['predicates']:
        saved_predicates.append(s_predicate)
        continue

    logging.info(f'Processing predicate ID: {s_predicate["id"]}')
    logging.info(f'Name: {s_predicate["details"]["name"]}')

    predicate = Predicate(s_predicate)

    # replace any tags with new ids
    # if we can't find an updated id, remove the tag
    if predicate.tags:
        updated_tags = []
        logging.info('fixing predicate tags')
        for index, tag in enumerate(predicate.tags):
            try:
                new_tag_id = tag_map[tag]
                updated_tags.append(new_tag_id)
                logging.info(f'Updated tag from {tag} to {new_tag_id}')
            except KeyError as e:
                logging.error(f'Could not find updated tag ID for tag: {tag}')
                logging.error('removing tag')
        predicate.tags = updated_tags

    # create the predicate
    res = s_client.create_predicate(predicate, test=True)
    predicate_map[s_predicate['id']] = res['id']
    predicate_cache[res['id']] = predicate
    logging.info(json.dumps(predicate.__dict__) + '\n')
logging.info('----- Non reference predicates complete -----\n')

# now process the predicates with references
# TODO: Make sure refs list isn't appended to the object
logging.info('----- Updating saved predicates -----')
while len(saved_predicates) > 0:
    s_predicate = saved_predicates.pop(0)
    # need to ensure all ref predicates have been created
    # and update ids to the newly created ids
    logging.info(f'Processing predicate ID: {s_predicate["id"]}')
    logging.info(f'Name: {s_predicate["details"]["name"]}')

    predicate = Predicate(s_predicate)

    # fix the predicates list, capture any globals in the process
    fix_error = 0
    logging.info('Updating predicate reference list')
    for ref in predicate.predicates:
        try:
            new_ref_id = predicate_map[ref['id']]
            logging.info(f'Changing ref id from {ref["id"]} to {new_ref_id}')
            ref['id'] = new_ref_id
        except KeyError:
            logging.warning(f'Could not find mapping for predicate: {ref["id"]}')
            # check to see if this is a global
            logging.info('Checking for global')
            tmp_predicate = s_client.get_predicate(ref['id'])
            if tmp_predicate:
                logging.info(f'Global found for predicate id: {ref["id"]}')
                logging.info('Updating maps')
                predicate_map[tmp_predicate['id']] = tmp_predicate['id']
            else:
                logging.error(f'Failed to find updated predicate ID for predicate {ref["id"]}')
                fix_error = 1

    # if we failed updating predicates, push to end of line continue to next
    if fix_error:
        logging.warning('Trying predicate later')
        saved_predicates.append(s_predicate)
        continue

    # fix the predicate refs in definition by searching for nested references
    logging.info('fixing predicate refs in definition')
    for entry in predicate.refs:
        new_ref_id = predicate_map[entry['$ref']]
        logging.info(f'Changing ref id from {entry["$ref"]} to {new_ref_id}')
        entry['$ref'] = new_ref_id
        
    # replace any tags with new ids
    # if we can't find an updated id, remove the tag
    if predicate.tags:
        updated_tags = []
        logging.info('fixing predicate tags')
        for index, tag in enumerate(predicate.tags):
            try:
                new_tag_id = tag_map[tag]
                updated_tags.append(new_tag_id)
                logging.info(f'Updated tag from {tag} to {new_tag_id}')
            except KeyError as e:
                logging.error(f'Could not find updated tag ID for tag: {tag}')
                logging.error('removing tag')
        predicate.tags = updated_tags


    # create the new predicate
    res = s_client.create_predicate(predicate, test=True)
    predicate_map[s_predicate['id']] = res['id']
    predicate_cache[res['id']] = predicate
    logging.info(json.dumps(predicate.__dict__) + '\n')
logging.info('----- Predicates with references complete -----\n')

# get rules
logging.info('----- Processing rules: -----')
rule_map = {}
s_rules = s_client.get_rules()
for s_rule in s_rules:
    logging.info(f'Fixing reference IDs for rule ID: {s_rule["id"]}')
    logging.info(f'Name: {s_rule["details"]["name"]}')
    rule = Rule(s_rule)

    # fix the predicate ID
    logging.info(f'Fixing referenced predicate ID')
    try:
        new_pred_id = predicate_map[rule.predicate['id']]
        logging.info(f'Updated predicate id from {rule.predicate["id"]} to {new_pred_id}')
        rule.predicate['id'] = new_pred_id
    except KeyError:
        logging.error(f'Could not find updated predicate id for predicate: {rule.predicate["id"]}')
        logging.error('skipping rule')
        continue

    # fix tags
    # replace any tags with new ids
    # if we can't find an updated id, remove the tag
    if rule.tags:
        updated_tags = []
        logging.info('Fixing tag IDs')
        for index, tag in enumerate(rule.tags):
            try:
                new_tag_id = tag_map[tag]
                updated_tags.append(new_tag_id)
                logging.info(f'Updated tag from {tag} to {new_tag_id}')
            except KeyError as e:
                logging.error(f'Could not find updated tag ID for tag: {tag}')
                logging.error('removing tag')
        rule.tags = updated_tags

    # fix target-group (notification) id
    # TODO: actions that tag matching activities 
    if rule.actions:
        updated_actions = []
        logging.info('Fixing Notification Policy IDs in actions')
        for action in rule.actions:
            try:
                target_id = action['parameters']['target']['id']
            except KeyError:
                # no targets in this action, keep and move on
                updated_actions.append(action)
                continue

            try:
                new_target_id = notify_policy_map[target_id]
                logging.info(f'Updating notification policy id from {target_id} to {new_target_id}')
                action['parameters']['target']['id'] = new_target_id
                updated_actions.append(action)
            except KeyError:
                logging.error(f'Could not find updated target ID in action, target ID: {target_id}')
                logging.error('removing action')

        rule.actions = updated_actions

    res = s_client.create_rule(rule, test=True)
    rule_map[s_rule['id']] = res['id']
    logging.info(json.dumps(rule.__dict__) + '\n')
logging.info('----- Rule procesing complete -----\n')

# get policies
s_policies = s_client.get_agent_policies()
logging.info('----- Updated Agent Policies: -----')
# TODO: add option create new agent policies from source tenant settings
for s_policy in s_policies:
    if s_policy['id']  not in update_agent_policies:
        continue

    logging.info(f'Processing Agent Policy with ID: {s_policy["id"]}')
    logging.info(f'Name: {s_policy["alias"]}')
    try:
        if s_policy['deleted'] == True:
            logging.warning('Skipping deleted policy')
            continue
    except KeyError:
        pass
    
    policy = Policy(s_policy)

    # update the rule ref ids
    try:
        refs = policy.policy['refs']
    except KeyError:
        logging.info('No rule references found in policy')
        continue

    updated_rule_list = []
    for rule in refs['rules']['rules']:
        try:
            new_rule_id = rule_map[rule['id']]
            logging.info(f'Updated rule ref id from {rule["id"]} to {new_rule_id}')
            rule['id'] = new_rule_id
            updated_rule_list.append(rule)
        except KeyError:
            # could not find a rule ref, should remove and report
            logging.error(f'Could not find an updated ref for rule id: {rule["id"]}')
            logging.error('Deleting rule reference from policy')
    policy.policy['refs']['rules']['rules'] = updated_rule_list
            
    # update the policy
    # TODO: need to use the target tenants policy id
    res = s_client.update_agent_policy(s_policy['id'], policy.policy, test=True)

    logging.info(json.dumps(policy.__dict__) + '\n')
logging.info('----- Agent policies complete -----\n')
