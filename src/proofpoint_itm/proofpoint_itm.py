import requests
import json

class ITMClient(object):
    def __init__(self, base_url, client_id, scope='*', verify=True, **kwargs):
        """ kwargs should contain either a username/password or a client_secret """
        self.client_id = client_id
        self.base_url = base_url
        if kwargs.get('username') and kwargs.get('password'):
            auth = {
                'username': kwargs.get('username'),
                'password': kwargs.get('password'),
                'grant_type': 'password'
            }
            self.grant_type = 'password'
        elif kwargs.get('client_secret'):
            auth = {
                'client_secret': kwargs.get('client_secret'),
                'grant_type': 'client_credentials'
            }
            self.grant_type = 'client_credentials'
        else:
            print('No suitable credentials supplied to access API, exiting')
            exit(1)
        
        auth['scope'] = scope
        self.verify = verify
        self.access_token = self.get_token(auth)

    def get_token(self, auth):
        endpoint = '/v2/apis/auth/oauth/token'
        url = self.base_url + endpoint
        payload = {
            'client_id': self.client_id,
            'grant_type': auth['grant_type'],
            'scope': auth['scope']
        }
        if 'username' in auth and 'password' in auth:
            payload['username'] = auth['username']
            payload['password'] = auth['password']
        elif 'client_secret' in auth:
            payload['client_secret'] = auth['client_secret']

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, headers=headers, data=payload, verify=self.verify)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print("Error retrieving token: {}".format(response.text))
            exit(1)

    def get_all_instances (self, includes='*'):
        endpoint = f'/v2/apis/registry/instances'

        params = {
            'limit': 100,
            'offset': 0,
            'includes': includes
        }

        endpoints = []
        resp = self._get_response('GET', endpoint, params=params)
        endpoints += resp['data']
        total = resp['_meta']['stats']['total']
        retrieved = len(endpoints)
        while retrieved < total:
            params['offset'] = params['offset'] + 100
            resp = self._get_response('GET', endpoint, params=params)
            endpoints += resp['data']
            retrieved = len(endpoints)
        
        return endpoints

    def get_predicate (self, id, includes='*'):
        endpoint = f'/v2/apis/depot/predicates/{id}'

        params = {
            'includes': includes
        }

        return self._get_response('GET', endpoint, params=params)

    def update_predicate(self, id, data):
        endpoint = f'/v2/apis/depot/predicates/{id}'
        return self._get_response('PUT', endpoint, data=data)

    def get_policies(self, params=None):
        endpoint = f'/v2/apis/registry/policies'
        return self._get_response('GET', endpoint, params=params)

    def get_policy(self, id, includes='*'):
        endpoint = f'/v2/apis/registry/policies/{id}'
        params = {
            'includes': includes
        }
        return self._get_response('GET', endpoint, params=params)
        

    def update_policy(self, id, data):
        endpoint = f'/v2/apis/registry/policies/{id}'
        return self._get_response('PATCH', endpoint, data=data)

    def overwrite_policy(self, id, data):
        endpoint = f'/v2/apis/registry/policies/{id}'
        return self._get_response('PUT', endpoint, data=data)

    def get_dictionaries(self, params=None):
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries'
        return self._get_response('GET', endpoint, params=params)

    def get_dictionary(self, id, includes='*'):
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        params = {
            'includes': includes
        }
        return self._get_response('GET', endpoint, params=params)

    def update_dictionary(self, id, data):
        endpoint = f'/v2/apis/ruler/configurations/dlp/dictionaries/{id}'
        return self._get_response('PATCH', endpoint, data=data)



    def get_activity(self, entities='event', data=''):
        """
        Queries activity API using export json from explortions
        Pass entity type with entities = event,casb,endpoint,audit
        or any combination of those values

        Pass the json query string as data
        """
        endpoint = '/v2/apis/activity/queries'

        params = {
            'limit': 100,
            'offset': 0,
            'entityTypes': entities,
        }

        events = []
        resp = self._get_response('POST', endpoint, params=params, data=data)
        events += resp['data']
        total = resp['_meta']['stats']['total']
        retrieved = len(events)
        while retrieved < total:
            params['offset'] = params['offset'] + 100
            resp = self._get_response('POST', endpoint, params=params, data=data)
            events += resp['data']
            retrieved = len(events)

        return events

    def _prepare_request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        req = requests.Request(method, url)

        headers = kwargs.get('headers', {})
        headers['Authorization'] = 'Bearer {}'.format(self.access_token)
        req.headers = headers

        params = kwargs.get('params', {})
        try:
            if len(params) > 0:
                req.params = params
        except TypeError:
            pass

        if method in ['PUT', 'POST', 'PATCH']:
            data = kwargs.get('data', {})
            req.json = data
        
        return req.prepare()


    def _get_response(self, type, endpoint, **kwargs):
        req = self._prepare_request(type, endpoint, **kwargs)
        if not hasattr(self, 'session'):
            self.session = requests.Session()
        resp = self.session.send(req,
            verify=self.verify
        )
        return resp.json()