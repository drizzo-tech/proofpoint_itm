from proofpoint_itm import webclient
from proofpoint_itm.auth import itm_auth
from proofpoint_itm.classes import Predicate,Rule,Tag,AgentPolicy,TargetGroup,Dictionary,Detector,DetectorSet
import uuid

class ITMClient(object):
    """ Client class for Proofpoint ITM SaaS API.
        
    This class shall be initialized with a config dictionary containing the
    client_id, tenant_id, and client_secret::

        {
            "tenant_id" : "The tenant name"
            "client_id" : "application client id"
            "client_secret": "client secret for token based auth"
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
                      headers: dict={}, count: bool=False) -> dict:
        """
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
            dict: A list of endpoint objects

        """
        endpoint = '/v2/apis/registry/instances'
        url = self.base_url + endpoint

        params = {'limit': 99,
                  'offset': 0,
                  'includes': includes,
                  'kind': kind,
                  'status': status
                 }

        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}

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


    def get_rules(self, includes: str='*', headers: dict={}) -> list:
        """ 
        Query for all rules in the depot API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            list: A list of rules objects

        """
        endpoint = '/v2/apis/ruler/rules'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_rule(self, id_: str, includes: str='*', headers: dict={}) -> dict:
        """
        Query for rule by ID in the depot API

        Args:
            id_ (str):
                Rule id to return, if not provided, return all
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            dict: A dict of rule attributes

        """
        endpoint = f'/v2/apis/ruler/rules/{id_}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp


    def update_rule(self, id_: str, rule: Rule, headers: dict={}, test: bool=False) -> dict:
        """
        Updates an existing rule from a proofpoint_itm.classes.Rule object

        Args:
            id_ (str):
                Rule ID to update
            rule (obj): 
                proofpoint_itm.classes.Rule object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            dict: A dictionary containing the API response.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/ruler/rules/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=rule.as_dict(), method='PUT')
        return resp


    def create_rule(self, rule: Rule, headers: dict={}, test=False) -> dict:
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
            dict: A dictionary containing the API response.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/ruler/rules'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        data = {'data': [rule.as_dict()]}
        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp


    def get_predicates(self, includes: str='*', headers: dict={}) -> list:
        """
        Query for all predicates in the depot API, does not return built-in

        Args:
            includes (str): 
                Comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            list: A list of predicate objects
        """
        endpoint = '/v2/apis/depot/predicates'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_predicate(self, id_: str, includes: str='*', headers: dict={}) -> dict:
        """
        Query for a single predicate by ID

        Args:
            id_ (str):
                The predicate id to return
            includes (str): 
                Comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict: A dict of predicate attributes
        """
        endpoint = f'/v2/apis/depot/predicates/{id_}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp


    def get_conditions(self, includes: str='*', headers: dict={}) -> list:
        """
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
            list: Returns list of predicate objects
        """
        conditions = []
        predicates = self.get_predicates(includes=includes, headers=headers)
        for predicate in predicates:
            if predicate['kind'] == 'it:predicate:custom:match':
                conditions.append(predicate)
        return conditions

    
    def update_predicate(self, id_, predicate: Predicate, headers: dict={}, test: bool=False) -> dict:
        """
        Update a predicate by ID. Performs a 'PATCH' method call to the depot/predicate API

        Args:
            id_ (str):
                ID of the predicate to udpate
            data (dict)
                A dict of the keys/values to update
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            dict: A dictionary containing the API response.
        """
        endpoint = f'/v2/apis/depot/predicates/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=predicate.as_dict(), method='PATCH')
        return resp

    def overwrite_predicate(self, id_, predicate: Predicate, headers: dict={}, test: bool=False) -> dict:
        """
        Overwrite a predicate by ID, Performs a 'PUT' method call to the depot/predicate API

        Args:
            id_ (str):
                ID of the predicate to udpate
            data (dict)
                A dict of the keys/values to update
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            dict: A dictionary containing the API response.
        """
        endpoint = f'/v2/apis/depot/predicates/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=predicate.as_dict(), method='PUT')
        return resp


    def create_predicate(self, predicate: Predicate, headers: dict={}, test: bool=False) -> dict:
        """
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
            dict: A dictionary containing the API response.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/predicates'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}

        data = {'data': [predicate.as_dict()]}
        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp


    def get_tags(self, includes: str='*', headers: dict={}) -> list:
        """
        Query for all tags in the depot API, does not return built-in tags

        Args:
            includes (str): Comma-separated list of attributes to include, default is '*'.
            headers (dict): Headers to include in the HTTP request, if not provided, a default header
                will be created with auth info.

        Returns: 
            list: A list of tags objects.

        """
        endpoint = '/v2/apis/depot/tags'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_tag(self, id_: str, includes: str='*', headers: dict={}) -> dict:
        """
        Get tag by ID.

        Args:
            id_ (str): The tag ID.
            includes (str): Comma-separated list of attributes to include. Default is '*'.
            headers (dict): Headers to include in the HTTP request. If not provided, a default header
                will be created with auth info.

        Returns:
            dict: A dictionary of tag information.

        """
        endpoint = f'/v2/apis/depot/tags/{id_}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp

    def update_tag(self, id_: str, tag: Tag, headers: dict={}, test: bool=False) -> dict:
        """
        Update a tag.

        Args:
            id_ (str): The ID of the tag to update.
            tag (Tag): The `proofpoint_itm.classes.Tag` object representing the updated tag.
            headers (dict, optional): Additional headers to include in the HTTP request.
                                    Defaults to an empty dictionary.
            test (bool, optional): A flag to indicate whether to return a fake generated UUID.
                                Defaults to False.

        Returns:
            dict: A dictionary containing the updated tag.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/tags/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=tag.as_dict(), method='PATCH')
        return resp

    def create_tag(self, tag: Tag, headers: dict={}, test: bool=False) -> dict:
        """
        Create a new tag.

        Args:
            tag (obj): The `proofpoint_itm.classes.Tag` object representing the tag to be created.
            headers (dict, optional): Additional headers to include in the HTTP request.
                                    If not provided, a default header will be created with auth info.
            test (bool, optional): Test flag to return a fake generated UUID. Defaults to False.

        Returns:
            dict: API response containing the created tag.

        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/depot/tags'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=tag.as_dict(), method='POST')
        return resp

    def add_activity_tag(self, fqid, tag_id, headers: dict={}) -> dict:
        """
        Add a tag to an activity.

        Parameters:
            fqid (str): The fully qualified ID of the activity to add the tag to.
            tag_id (str): The ID of the tag to be added.
            headers (dict, optional): Additional headers to include in the HTTP request.
                                    Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f'/v2/apis/activity/events/{fqid}'
        params = {'tagValue': tag_id}
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, method='PATCH', params=params)
        return resp
    
    def add_activity_assignee(self, fqid, admin_id, headers: dict={}) -> dict:
        """
        Adds an assignee to an activity.

        Args:
            fqid (str): The fully qualified ID of the activity to add the assignee to.
            admin_id (str): The admin ID that will be assigned to the activity.
            headers (dict, optional): Additional headers to include in the HTTP request.
                                    Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f'/v2/apis/activity/events/{fqid}/annotations/workflow/assignment'
        body = {'id': admin_id}
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, method='POST', json_data=body)
        return resp

    def get_agent_policies(self, includes: str='*', headers: dict={}, params: dict=None) -> list:
        """
        Retrieves agent policies from the specified API endpoint.

        Args:
            includes (str, optional): A string specifying the entities to include in the response. Defaults to '*',
                                    which includes all entities.
            headers (dict, optional): Additional headers to be included in the request. Defaults to an empty dictionary.
            params (dict, optional): Additional parameters to control the request, such as 'limit' and 'offset'.
                                    Defaults to None.

        Returns:
            list: A list containing the retrieved agent policies.
        """
        endpoint = '/v2/apis/registry/policies'
        url = self.base_url + endpoint
        if params is None:
            params = {'limit': 99, 'offset': 0, 'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_agent_policy(self, id_: str, includes: str='*', headers: dict={}, params: dict=None) -> dict:
        """
        Retrieves a specific agent policy based on the provided ID from the specified API endpoint.

        Args:
            id_ (str): The ID of the agent policy to retrieve.
            includes (str, optional): A string specifying the entities to include in the response. Defaults to '*',
                                    which includes all entities.
            headers (dict, optional): Additional headers to be included in the request. Defaults to an empty dictionary.
            params (dict, optional): Additional parameters to control the request, such as 'limit' and 'offset'.
                                    Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved agent policy.
        """
        endpoint = f'/v2/apis/registry/policies/{id_}'
        url = self.base_url + endpoint
        if params is None:
            params = {'limit': 99, 'offset': 0, 'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def update_agent_policy(self, id_, policy: AgentPolicy, headers: dict={}, test: bool=False) -> dict:
        """
        Update an Agent Policy by ID
        
        Args:
            id_ (str):
                ID of the policy to update
            policy (AgentPolicy):
                A proofpoint_itm.classes.AgentPolicy object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake success status

        Returns:
            dict: A dictionary containing the updated agent policy.
        """
        if test:
            return {'status': 200, 'msg': 'success'}
        endpoint = f'/v2/apis/registry/policies/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, json_data=policy.as_dict(), method='PATCH')
        return resp

    def overwrite_agent_policy(self, id_, policy: AgentPolicy, headers: dict={}, test: bool=False) -> dict:
        """
        Overwrite an Agent Policy by ID

        Args:
            id_ (str):
                ID of the policy to update
            policy (AgentPolicy):
                A proofpoint_itm.classes.AgentPolicy object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake success status

        Returns:
            dict: A dictionary containing the updated agent policy.
        """
        if test:
            return {'status': 200, 'msg': 'success'}
        endpoint = f'/v2/apis/registry/policies/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, json_data=policy.as_dict(), method='PUT')
        return resp

    def create_agent_policy(self, policy: AgentPolicy, headers: dict={}, test: bool=False) -> dict:
        """
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
            dict: A dictionary containing the created agent policy.
        """
        if test:
            return {'status': 200, 'msg': 'success'}
        endpoint = f'/v2/apis/registry/policies'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, json_data=policy.as_dict(), method='POST')
        return resp


    def get_notification_policies(self, includes='*', headers={}) -> list:
        """
        Query for all notification policies in the notifications API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns: 
            list: A list containing notification policies
        """
        endpoint = '/v2/apis/notification/target-groups'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def update_notification_policy(self, id_: str, target_group: TargetGroup, headers: dict={}, test: bool=False) -> dict:
        """Update existing notification policy (target-group)

        Updates an existing notification policy from a proofpoint_itm.classes.TargetGroup object

        Args:
            id_ (str)
                The target-group ID to update
            target_group (obj):
                proofpoint_itm.classes.TargetGroup object
            headers (dict): 
                headers to include in the http request, if not provided
                a default header will be created with auth info
            test (bool):
                Test flag to return fake generated uuid

        Returns:
            dict: A dictionary containing the updated notification policy.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = f'/v2/apis/notification/target-groups/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=target_group.as_dict(), method='PATCH')
        return resp


    def create_notification_policy(self, target_group: TargetGroup, headers: dict={}, test: bool=False) -> dict:
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
            dict: A dictionary containing the created notification policy.
        """
        if test:
            return {'id': str(uuid.uuid4())}
        endpoint = '/v2/apis/notification/target-groups'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        data = [target_group.as_dict()]
        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp

    def get_dictionaries(self, headers: dict={}, includes: str='*') -> list:
        """
        Retrieve dictionaries from the API endpoint.

        Args:
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            includes (str, optional): A string specifying the entities to include in the response.
                Defaults to '*', which includes all entities.

        Returns:
            list: A list containing the retrieved dictionaries.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_dictionary(self, id_: str, headers: dict={}, include: str=None) -> dict:
        """
        Retrieve a specific dictionary from the API endpoint.

        Args:
            id_ (str): The ID of the dictionary to retrieve.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            include (str, optional): A string specifying the entities to include in the response.
                Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved dictionary.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id_}'
        url = self.base_url + endpoint
        params = {}
        if include is not None:
            params['include'] = include
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']


    def get_dictionary_terms(self, id_: str, headers: dict={}, includes: str='*') -> list:
        """
        Retrieve terms from a specific dictionary in the API endpoint.

        Args:
            id_ (str): The ID of the dictionary to retrieve terms from.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            includes (str, optional): A string specifying the entities to include in the response.
                Defaults to '*', which includes all entities.

        Returns:
            list: A list containing the retrieved terms.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id_}/entries'
        url = self.base_url + endpoint
        params = {'includes': includes}
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.get_request(url, headers=headers, params=params)
        return resp['data']
    

    def update_dictionary(self, id_: str, dictionary: Dictionary, headers: dict={}) -> dict:
        """
        Update a dictionary.

        Args:
            id_ (str): The ID of the dictionary to update.
            dictionary (Dictionary): The `Dictionary` object representing the updated dictionary.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the updated dictionary.

    """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        resp = webclient.post_request(url, headers=headers, json_data=dictionary.as_dict(), method='PATCH')
        return resp


    def create_dictionary(self, dictionary: Dictionary, headers: dict={}) -> dict:
        """
        Create a new dictionary.

        Args:
            dictionary (Dictionary): The `proofpoint_itm.classes.Dictionary` object representing
                the new dictionary to be created.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the created dictionary.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.post_request(url, headers=headers, json_data=dictionary.as_dict(), method='POST')
        return resp

    def create_dictionaries(self, dictionaries: list=[], headers: dict={}) -> list:
        """
        Creates or updates a batch list of dictionaries

        Args:
            dictionaries (list): A list of proofpoint_itm.classes.Dictionary objects
            headers (dict): Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            list: A list containing the created dictionaries.
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        dictionary_list = [d.as_dict() for d in dictionaries]
        data = { 'data': dictionary_list }
        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def delete_dictionary(self, id_: str, headers: dict={}) -> dict:
        """
        Delete a dictionary.

        Args:
            id_ (str): The ID of the dictionary to delete.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id_}'
        url = self.base_url + endpoint
        headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        resp = webclient.delete_request(url, headers=headers)
        return resp


    def update_event_workflow(self, fqid: str, status: str, headers: dict={}) -> dict:
        """Update workflow status of an alert/incident
        
        Args:
            fqid_ (str): The fqid of an event/incident
            status (str): The new status to be applied to the incident
                Accepts new, reopened, in-progress, escalated, on-hold,
                resolved, false-positive, not-an-issue

        Returns:
            dict: A dictionary containing the API response.
        """
        endpoint = f'/v2/apis/activity/events/{fqid}/annotations/workflow'
        url = self.base_url + endpoint
        data = {
            'state': {
                'status': f'incident:status:{status}'
            }
        }
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def get_detectors(self, headers: dict={}) -> list:
        """
        Retrieve detectors from the API endpoint.

        This method retrieves detectors related to DLP configurations from the specified API endpoint.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            list: A list containing the retrieved detectors.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/detectors'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def get_detector(self, id_: str, headers: dict={}) -> dict:
        """
        Retrieve a specific detector from the API endpoint.

        Args:
            id_ (str):
                The ID of the detector to retrieve.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the retrieved detector.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectors/{id_}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp

    def update_detector(self, id_: str, detector: Detector, headers: dict={}) -> dict:
        """
        This method updates an existing detector with the provided ID based on a `Detector` object.

        Args:
            id_ (str):
                The ID of the detector to update.
            detector (Detector):
                The `Detector` object representing the updated detector.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectors/{id_}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector.as_dict(), method='PATCH')
        return resp

    def create_detector(self, detector: Detector, headers: dict={}) -> dict:
        """
        Create a new detector.

        Args:
            detector (Detector):
                The `Detector` object representing the new detector to be created.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/detectors'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector.as_dict(), method='POST')
        return resp

    def get_detector_sets(self, headers: dict={}) -> list:
        """
        Retrieve detector sets from the API endpoint.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            list: A list containing the retrieved detector sets.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/detectorsets'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def get_detector_set(self, id_: str, headers: dict={}) -> dict:
        """
        Retrieve a specific detector set from the API endpoint based on the provided ID.

        Args:
            id_ (str):
                The ID of the detector set to retrieve.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the retrieved detector set.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id_}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp

    def update_detector_set(self, id_: str, detector_set: DetectorSet, headers: dict={}) -> dict:
        """
        Update a detector set with the provided ID based on a `DetectorSet` object.

        Args:
            id_ (str):
                The ID of the detector set to update.
            detector_set (DetectorSet):
                The `DetectorSet` object representing the updated detector set.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the updated detector set.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id_}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector_set.as_dict(), method='PATCH')
        return resp

    def create_detector_set(self, detector_set: DetectorSet, headers: dict={}) -> dict:
        """
        Create a new detector set.

        Args:
            detector_set (DetectorSet):
                The `DetectorSet` object representing the new detector set to be created.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the created detector set.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/detectorsets'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=detector_set.as_dict(), method='POST')
        return resp
    
    def delete_detector_set(self, id_: str, headers: dict={}) -> dict:
        """
        Delete a detector set.

        Args:
            id_ (str):
                The ID of the detector set to delete.
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/detectorsets/{id_}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.delete_request(url, headers=headers)
        return resp

    def get_smartids(self, headers: dict={}) -> list:
        """
        Retrieve smart IDs from the API endpoint.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the retrieved smart IDs.

        """
        endpoint = '/v2/apis/ruler/configurations/dlp/smartids'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.get_request(url, headers=headers)
        return resp['data']

    def publish_config(self, headers: dict={}, artifactID: str='activity', data: dict={}) -> dict:
        """
        This method publishes a configuration artifact triggers a configuration push.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            artifactID (str, optional):
                The ID of the artifact to publish. Defaults to 'activity'.
            data (dict, optional):
                The configuration data to publish. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.
            
        """
        endpoint = f'/v2/apis/ruler/artifacts/{artifactID}'
        url = self.base_url + endpoint
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, method='PUT', json_data=data)
        return resp

    def depot_search(self, query: dict, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the depot API

        Args:
            query (dict):
                A dict representing an Elasticsearch query, will be converted to json string
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
            dict: A dictionary containing the API response.

        """
        endpoint = '/v2/apis/depot/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp

    def notification_search(self, query: dict, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the depot API

        Args:
            query (dict):
                A dict representing an Elasticsearch query, will be converted to json string
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
            dict: A dictionary containing the API response.

        """
        endpoint = '/v2/apis/notification/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp

    def ruler_search(self, query: str, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the ruler API

        Args:
            query (dict):
                A dict representing an Elasticsearch query, will be converted to json string
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
            dict: A dictionary containing the API response.

        """
        endpoint = '/v2/apis/ruler/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp

    def activity_search(self, query: dict, entity: str, params: dict={}, headers: dict={}) -> dict:
        """
        Performs a search query against the activity API

        Args:
            query (dict):
                A dict representing an Elasticsearch query, will be converted to json string
            entity (str):
                entityTypes to search for
                Accepted values: event, casbevent, audit, network
            params (dict):
                A dict of web request url parameters
                ex. offset = 0, limit=500
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = '/v2/apis/activity/queries'
        url = self.base_url + endpoint
        params['entityTypes'] = entity
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp
    
    def registry_search(self, query: dict, entity: str, params: dict = None, headers: dict = None ) -> dict:
        """
        Performs a search query against the registry API

        Args:
            query (dict):
                A dict representing an Elasticsearch query, will be converted to json string
            entity (str):
                entityTypes to search for
                Accepted values: event, casbevent, audit, network
            params (dict):
                A dict of web request url parameters
                ex. offset=0, limit=500
            headers (dict):
                Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            dict: A dictionary containing the API response.

        """
        url = self.base_url + '/v2/apis/registry/queries'
        if params is None:
            params = {}
        params['entityTypes'] = entity

        if headers is None:
            headers = {}
        headers['Authorization'] = f"{self.auth.token['token_type']} {self.auth.access_token}"

        resp = webclient.post_request(url, headers=headers, json_data=query, method='POST', params=params)
        return resp