from proofpoint_itm import webclient
from proofpoint_itm.auth import itm_auth
from proofpoint_itm.classes import Predicate,Rule,Tag,AgentPolicy,TargetGroup,Dictionary,Detector,DetectorSet
import uuid

class ITMClient(object):
    """ Client class for Proofpoint ITM SaaS API.
        
    This class shall be initialized with a config dictionary containing the
    following information:
        {
            "tenant_id" : "<The tenant name>"
            "client_id" : "<application client id>"
            "client_secret": "<client secret for token based auth>"
        }
    """
    
    def __init__(self, config, scope='*', verify=True, **kwargs):
        """Initialization

        Initial ITMClient class object

        Args:
            config (dict): 
                Required positional arg, contains tenant_id, client_id,
                client_secret
            scope (str):
                Scope of the API requests, defaults to '*'
            verify (bool):
                Sets requests option to verify certificates

        Returns:
            ITMClient object
        """
        self.client_id = config['client_id']
        self.tenant_id = config['tenant_id']
        self.base_url = f"https://{config['tenant_id']}.explore.proofpoint.com"
        self.auth = itm_auth(config, verify=verify, scope=scope)

    
    def get_endpoints(self, includes: str='*', kind: str='*', status: str='*',
                      headers: dict=None, count: bool=False) -> dict:
        """Gets endpoints from the registry API

        Fetches all endpoints of a given kind from the registry api

        Args:
            includes (str):
                List of attributes to return, defaults to *
            kind (str): 
                Type of agent to return,
                Accepts *, agent:saas, or updater:saas, defaults to *
            status (str): 
                Filter by agent status
                Accepts: *, HEALTHY, UNHEALTHY, UNREACHABLE, DEAD, INACTIVE

        Returns:
            A list of endpoint objects
        """
        endpoint = '/v2/apis/registry/instances'
        url = self.base_url + endpoint

        params = {'limit': 99,
                  'offset': 0,
                  'includes': includes,
                  'kind': kind,
                  'status': status
                 }

        if headers is None:
            headers = {
                'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}

        endpoints = []
        resp = webclient.get_request(
                url, headers=headers, params=params)
        total = resp['_meta']['stats']['total']

        if count:
            return total

        endpoints += resp['data']
        retrieved = len(endpoints)

        while retrieved < total:
            params['offset'] = params['offset'] + 100
            resp = webclient.get_request(
                    url, headers=headers, params=params)
            endpoints += resp['data']
            retrieved = len(endpoints)
        
        return endpoints


    def get_rules(self, includes: str='*', headers: dict=None) -> list:
        """Get all rules 

        Query for all rules in the depot API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A list of rules objects
        """
        endpoint = '/v2/apis/ruler/rules'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_rule(self, id: str, includes: str='*', headers: dict=None) -> dict:
        """Get rule by ID 

        Query for rule by ID in the depot API

        Args:
            id (str):
                Rule id to return, if not provided, return all
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A dict of rule attributes
        """
        endpoint = f'/v2/apis/ruler/rules/{id}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp


    def update_rule(self, id: str, rule: Rule, headers: dict=None, test: bool=False) -> dict:
        """Update existing rule

        Updates an existing rule from a proofpoint_itm.classes.Rule object

        Args:
            id (str):
                Rule ID to update
            rule (obj): 
                proofpoint_itm.classes.Rule object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response text
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/ruler/rules/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=rule.as_dict(), method='PUT')
        return resp


    def create_rule(self, rule: Rule, headers=None, test=False):
        """Create new rule

        Creates a new rule from a proofpoint_itm.classes.Rule object

        Args:
            rule (obj): 
                proofpoint_itm.classes.Rule object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response text
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/ruler/rules'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        data = {'data': [rule.as_dict()]}

        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp


    def get_predicates(self, includes: str='*', headers: dict=None) -> list:
        """Get all predicates

        Query for all predicates in the depot API, does not return built-in

        Args:
            includes (str): 
                Comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A list of predicate objects
        """
        endpoint = '/v2/apis/depot/predicates'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_predicate(self, id: str, includes: str='*', headers: dict=None) -> dict:
        """Query for a single predicate

        Query for a single predicate by ID

        Args:
            id (str):
                The predicate id to return
            includes (str): 
                Comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            A dict of predicate attributes
        """
        endpoint = f'/v2/apis/depot/predicates/{id}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp


    def get_conditions(self, includes: str='*', headers: dict=None) -> list:
        """Queries for custom conditions (predicates) created by users

        Query for all custom match predicates (user created) that are not auto
        created from rules

        Uses the get_predicates call, then post filters for kind = it:predicate:custom:match

        Args:
            includes (str): 
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            Returns list of predicate objects
        """
        conditions = []
        predicates = self.get_predicates(includes=includes, headers=headers)
        for predicate in predicates:
            if predicate['kind'] == 'it:predicate:custom:match':
                conditions.append(predicate)
        return conditions

    
    def update_predicate(self, id, predicate: Predicate, headers=None, test=False):
        """Update a predicate by ID

        Args:
            id (str):
                ID of the predicate to udpate
            data (dict)
                A dict of the keys/values to update
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        endpoint = f'/v2/apis/depot/predicates/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        
        resp = webclient.post_request(url, headers=headers, json_data=predicate.as_dict(), method='PUT')
        return resp


    def create_predicate(self, predicate: Predicate, headers: dict=None, test: bool=False) -> dict:
        """Create new predicate

        Creates a new predicate from a proofpoint_itm.classes.Predicate object

        Args:
            predicate (obj):
                proofpoint_itm.classes.Predicate object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/predicates'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        data = {'data': [predicate.as_dict()]}

        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp


    def get_tags(self, includes: str='*', headers: dict=None) -> list:
        """Get all tags

        Query for all tags in the depot API, does not return built-in

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A list of tags objects
        """
        endpoint = '/v2/apis/depot/tags'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_tag(self, id: str, includes: str='*', headers: dict=None) -> dict:
        """Get tag by ID

        Query for specific tag ID in the depot API

        Args:
            id (str):
                The tag ID
            includes (str): 
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A dict of tags info (dict)
        """
        endpoint = f'/v2/apis/depot/tags/{id}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp

    def update_tag(self, id: str, tag: Tag, headers: dict=None, test: bool=False) -> dict:
        """Update existing tag

        Update existing tag from a proofpoint_itm.classes.Tag object

        Args:
            id (str):
                id of the target tag to update
            tag (obj):
                proofpoint_itm.classes.Tag object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/tags/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        resp = webclient.post_request(url, headers=headers, json_data=tag.as_dict(), method='PATCH')
        return resp

    def create_tag(self, tag: Tag, headers: dict=None, test: bool=False) -> dict:
        """Create new tag

        Creates a new tag from a proofpoint_itm.classes.Tag object

        Args:
            tag (obj):
                proofpoint_itm.classes.Tag object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/tags'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        resp = webclient.post_request(url, headers=headers, json_data=tag.as_dict(), method='POST')
        return resp


    def get_agent_policies(self, includes: str='*', headers: dict=None, params: dict=None) -> dict:
        endpoint = '/v2/apis/registry/policies'
        url = self.base_url + endpoint
        if params is None:
            params = {'limit': 99, 'offset': 0, 'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_agent_policy(self, id: str, includes: str='*', headers: dict=None, params: dict=None) -> dict:
        endpoint = f'/v2/apis/registry/policies/{id}'
        url = self.base_url + endpoint
        if params is None:
            params = {'limit': 99, 'offset': 0, 'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def update_agent_policy(self, id, policy: AgentPolicy, headers: dict=None, test: bool=False) -> dict:
        """Update an Agent Policy by ID

        Update an agent policy
        
        Args:
            id (str):
                ID of the policy to update
            policy (AgentPolicy):
                A proofpoint_itm.classes.AgentPolicy object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake success status

        Returns:
            API response (dict)
        """
        if test:
            return {'status': 200, 'msg': 'success'}
        endpoint = f'/v2/apis/registry/policies/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.post_request(url, headers=headers, json_data=policy.as_dict(), method='PUT')
        return resp

    def create_agent_policy(self, policy: AgentPolicy, headers: dict=None, test: bool=False) -> dict:
        """Create an Agent Policy

        Create an new agent policy from a proofpoint_itm.classes.AgentPolicy object
        
        Args:
            policy (AgentPolicy):
                A proofpoint_itm.classes.AgentPolicy object to create
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake success status

        Returns:
            API response (dict)
        """
        if test:
            return {'status': 200, 'msg': 'success'}
        endpoint = f'/v2/apis/registry/policies'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.post_request(url, headers=headers, json_data=policy.as_dict(), method='POST')
        return resp


    def get_notification_policies(self, includes='*', headers=None):
        """Get all notification policies

        Query for all notification policies in the notifications API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            A dict of tags
        """
        endpoint = '/v2/apis/notification/target-groups'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def update_notification_policy(self, id: str, target_group: TargetGroup, headers: dict=None, test: bool=False) -> dict:
        """Update existing notification policy (target-group)

        Updates an existing notification policy from a proofpoint_itm.classes.TargetGroup object

        Args:
            id (str)
                The target-group ID to update
            target_group (obj):
                proofpoint_itm.classes.TargetGroup object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/notification/target-groups/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        resp = webclient.post_request(url, headers=headers, json_data=target_group.as_dict(), method='PATCH')
        return resp


    def create_notification_policy(self, target_group: TargetGroup, headers: dict=None, test: bool=False) -> dict:
        """Create new notification policy (target-group)

        Creates a new notification policy from a proofpoint_itm.classes.TargetGroup object

        Args:
            target_group (obj):
                proofpoint_itm.classes.TargetGroup object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            API response (dict)
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = '/v2/apis/notification/target-groups'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}

        data = [target_group.as_dict()]

        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp

    def get_dictionaries(self, headers: dict=None, includes: str='*') -> dict:
        """
        Queries for user defined dictionaries

        Returns dict of dictionaries
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_dictionary(self, id: str, headers: dict=None, include: str=None) -> dict:
        """
        Queries for user defined dictionaries

        Returns json as dict
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        url = self.base_url + endpoint
        params = {}
        if include is not None:
            params['include'] = include
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_dictionary_terms(self, id: str, headers: dict=None, includes: str='*') -> dict:
        """
        Queries for entries/terms in specific user defined dictionary

        Returns dict dictionary entries
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}/entries'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']
    

    def update_dictionary(self, id: str, dictionary: Dictionary, headers: dict=None) -> dict:
        """Update existing dictionary

        Updates an existing user defined dictionary by ID

        Args:
            id (str):
                dictionary ID
            dictionary (Dictionary):
                A proofpoint_itm.classes.Dictionary object
            headers (dict):
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            API Response as dict
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        
        resp = webclient.post_request(url, headers=headers, json_data=dictionary.as_dict(), method='PATCH')
        return resp


    def create_dictionary(self, dictionary: Dictionary, headers: dict=None) -> dict:
        """Create new dictionary
        
        Creates a new user defined dictionary

        Args:
            dictionary (Dictionary):
                A proofpoint_itm.classes.Dictionary object
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            API response as dict
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.post_request(url, headers=headers, json_data=dictionary.as_dict(), method='POST')
        return resp

    def create_dictionaries(self, dictionaries: list=[], headers: dict=None):
        """
        Creates or updates a batch list of dictionaries

        Args:
            dictionaries (list):
                A list of proofpoint_itm.classes.Dictionary objects
            headers (dict):
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            webclient response
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        dictionary_list = [d.as_dict() for d in dictionaries]
        data = { 'data': dictionary_list }
        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def delete_dictionary(self, id: str, headers: dict=None) -> dict:
        """
        Deletes a dictionary by ID

        Returns response as dict
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.delete_request(url, headers=headers)
        return resp


    def update_event_workflow(self, fqid: str, status: str, headers: dict={}):
        """Update workflow status of an alert/incident
        
        Args:
            fqid (str):
                The fqid of an event/incident
            status (str):
                The new status to be applied to the incident
                Accepts new, reopened, in-progress, escalated, on-hold,
                        resolved, false-positive, not-an-issue

        Returns:
            urllib.response object
        """
        endpoint = f'/v2/apis/activity/events/{fqid}/annotations/workflow'
        url = self.base_url + endpoint

        data = {
            'state': {
                'status': f'incident:status:{status}'
            }
        }

        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}

        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def get_detectors(self, headers: dict={}) -> dict:
        endpoint = '/v2/apis/ruler/configurations/dlp/detectors'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def get_detector(self, id: str, headers: dict={}) -> dict:
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectors/{id}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp

    def update_detector(self, id: str, detector: Detector, headers: dict={}):
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectors/{id}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector.as_dict(), method='PATCH')
        return resp

    def create_detector(self, detector: Detector, headers: dict={}):
        endpoint = '/v2/apis/ruler/configurations/dlp/detectors'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector.as_dict(), method='POST')
        return resp

    def get_detector_sets(self, headers: dict={}) -> dict:
        endpoint = '/v2/apis/ruler/configurations/dlp/detectorsets'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def get_detector_set(self, id: str, headers: dict={}) -> dict:
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp

    def update_detector_set(self, id: str, detector_set: DetectorSet, headers: dict={}):
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector_set.as_dict(), method='PATCH')
        return resp

    def create_detector_set(self, detector_set: DetectorSet, headers: dict={}):
        endpoint = '/v2/apis/ruler/configurations/dlp/detectorsets'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector_set.as_dict(), method='POST')
        return resp
    
    def delete_detector_set(self, id: str, headers: dict={}):
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.delete_request(url, headers=headers)
        return resp

    def get_smartids(self, headers: dict={}) -> dict:
        endpoint = '/v2/apis/ruler/configurations/dlp/smartids'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def depot_search(self, query: str, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the depot API

        Args:
            query (dict):
                A dict representing an Elastic Search query, will be converted to json string
            entity (str):
                entityTypes to search for
                Accepted values: list, predicate, tag, article
            params (dict):
                A dict of web request url parameters
                ex. offset = 0, limit=500
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict of returned objects

        """
        endpoint = '/v2/apis/depot/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp['data']

    def notification_search(self, query: dict, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the depot API

        Args:
            query (dict):
                A dict representing an Elastic Search query, will be converted to json string
            entity (str):
                entityTypes to search for
                Accepted values: target-group, notification
            params (dict):
                A dict of web request url parameters
                ex. offset = 0, limit=500
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict of returned objects

        """
        endpoint = '/v2/apis/notification/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp['data']

    def ruler_search(self, query: str, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the ruler API

        Args:
            query (dict):
                A dict representing an Elastic Search query, will be converted to json string
            entity (str):
                entityTypes to search for
                Accepted values: artifact, rule, rulechain
            params (dict):
                A dict of web request url parameters
                ex. offset = 0, limit=500
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict of returned objects

        """
        endpoint = '/v2/apis/ruler/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp['data']