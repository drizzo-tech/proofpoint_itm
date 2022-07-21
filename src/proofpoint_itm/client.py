from proofpoint_itm import webclient
from proofpoint_itm.auth import itm_auth

class ITMClient(object):
    """ Client class for Proofpoint ITM SaaS API
        
    This class shall be initialized with a config dictionary containing the
    following information
        {
            "tenant_id" : "The tenant name"
            "client_id" : "application client id"
            "client_secret": "Client secret for token based auth (optional)"
        }
    """
    
    def __init__(self, config, scope='*', verify=True, **kwargs):
        """
        Initialization
        """
        self.client_id = config['client_id']
        self.tenant_id = config['tenant_id']
        self.base_url = f"https://{config['tenant_id']}.explore.proofpoint.com"
        self.auth = itm_auth(config, verify=verify, scope=scope)

    
    def get_endpoints(self, includes='*', kind='*', status='*',
                      headers=None, count=False):
        """Gets endpoints from the registry API

        Fetches all endpoints of a given kind from the registry api

        Args:
            includes (str): List of attributes to return, defaults to *
            kind (str): Type of agent to return
              Accepts *, agent:saas, or updater:saas, defaults to *
            status (str): Filter by agent status
              Accepts: *, HEALTHY, UNHEALTHY, UNREACHABLE, DEAD, INACTIVE

        Returns:
            A dict of endpoint objects
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
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}

        endpoints = []
        resp = webclient.get_request(url, headers=headers, query_params=params)
        total = resp['_meta']['stats']['total']

        if count:
            return total

        endpoints += resp['data']
        retrieved = len(endpoints)

        while retrieved < total:
            params['offset'] = params['offset'] + 100
            resp = webclient.get_request(url, headers=headers, query_params=params)
            endpoints += resp['data']
            retrieved = len(endpoints)
        
        return endpoints
    

    def get_predicates(self, id=None, includes='*', headers=None):
        """
        Query for all predicates or specific predicate by id in the depot API

        Returns dict of predicates
        """
        endpoint = '/v2/apis/depot/predicates'
        if id:
            endpoint = endpoint + f'/{id}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, query_params=params)
        return resp['data']

    
    def update_predicate(self, id, data, headers=None):
        endpoint = f'/v2/apis/depot/predicates/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        
        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def get_conditions(self):
        """
        Queries for custom conditions created by users

        Returns dict of conditions
        """
        conditions = []
        predicates = self.get_predicates(includes='*')
        for predicate in predicates:
            if predicate['kind'] == 'it:predicate:custom:match':
                conditions.append(predicate)
        return conditions


    def get_policies(self, includes='id,alias,kind,details', headers=None):
        endpoint = '/v2/apis/registry/policies'
        url = self.base_url + endpoint
        params = {'limit': 99, 'offset': 0, 'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, query_params=params)
        return resp['data']


    def get_dictionaries(self, id=None, headers=None, includes='*'):
        """
        Queries for user defined dictionaries

        Returns dict of dictionaries
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        if id:
            endpoint = endpoint + f'/{id}'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, query_params=params)
        return resp['data']


    def get_dictionary_terms(self, id, headers=None, includes='*'):
        """
        Queries for entries/terms in specific user defined dictionary

        Returns dict dictionary entries
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}/entries'
        url = self.base_url + endpoint
        params = {'includes': includes}
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.get_request(url, headers=headers, query_params=params)
        return resp['data']
    

    def update_dictionary(self, id, data, headers=None):
        """
        Updates an existing user defined dictionary by ID

        id = dictionary ID
        data = dict representing a dictionary

        example:
        {
            "name": "dictionary 1",
            "description": "dictionary 1 description",
            "entries": [
                {
                    "term": "term1",
                    "type": "CaseSensitive",
                    "weight": 5,
                    "count": 1
                }
            ]
        } 
        """
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}",}
        
        resp = webclient.post_request(url, headers=headers, json_data=data, method='PATCH')
        return resp


    def create_dictionary(self, data, headers=None):
        """
        Creates a new user defined dictionary

        data = dict representing a dictionary

        example:
        {
            "name": "dictionary 1",
            "description": "dictionary 1 description",
            "entries": [
                {
                    "term": "term1",
                    "type": "CaseSensitive",
                    "weight": 5,
                    "count": 1
                }
            ]
        } 
        """
        endpoint = '/v2/apis/ruler/configurations/dlp/dictionaries'
        url = self.base_url + endpoint
        if headers is None:
            headers = {'Authorization': f"{self.auth.token['token_type']} {self.auth.access_token}"}
        
        resp = webclient.post_request(url, headers=headers, json_data=data, method='POST')
        return resp


    def delete_dictionary(self, id, headers=None):
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


    def update_event_workflow(self, fqid, status, headers=None):
        """Update workflow status of an alert/incident
        
        Args:
            fqid (str): The fqid of an event/incident
            status (str): The new status to be applied to the incident
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
