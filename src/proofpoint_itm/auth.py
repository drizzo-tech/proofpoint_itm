from proofpoint_itm import webclient

class itm_auth:
    """
    Basic class to represent API Auth Info
    """
    def __init__(self, config, verify=True, scope='*', grant_type='client_credentials'):
        self.tenant_id = config['tenant_id']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.scope = scope
        self.grant_type = grant_type
        self.verify = verify
        self.token = self.get_token()
        self.access_token = self.token['access_token']

    def get_token(self):
        endpoint = '/v2/apis/auth/oauth/token'
        base_url = f"https://{self.tenant_id}.explore.proofpoint.com"
        url = base_url + endpoint

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': self.grant_type,
            'scope': self.scope
        }

        resp = webclient.post_request(url, headers=headers, data=payload)
        token = {
            'access_token': resp['access_token'],
            'token_type': resp['token_type'],
            'expires_in': resp['expires_in'],
            'refresh_token': resp['refresh_token']
        }
        return token

    def refresh_token(self):
        pass
