from proofpoint_itm.classes import (
    Predicate,
    Rule,
    Tag,
    AgentPolicy,
    TargetGroup,
    Dictionary,
    Detector,
    DetectorSet,
)
import uuid
import requests


class ITMClient(object):
    """Client class for Proofpoint ITM SaaS API.

    This class shall be initialized with a config dictionary containing the
    client_id, tenant_id, and client_secret::

        {
            "tenant_id" : "The tenant name"
            "client_id" : "application client id"
            "client_secret": "client secret for token based auth"
        }

    """

    def __init__(self, config, scope="*", verify=True, development=False, **kwargs):
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
            developement (bool):
                Enable development mode, no API calls are sent, returns web request details only

        Returns:
            ITMClient object
        """
        self.client_id = config["client_id"]
        self.tenant_id = config["tenant_id"]
        self.client_secret = config["client_secret"]
        self.base_url = f"https://{self.tenant_id}.explore.proofpoint.com/v2/apis"
        self.development_mode = development
        self.timeout = kwargs.get("timeout", 30)

        token = self.get_token()
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token['access_token']}"})
        self.session.verify = verify

    def get_token(self):
        endpoint = "auth/oauth/token"
        form = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "*",
        }
        try:
            resp = requests.post(self.build_url(endpoint), data=form)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to get token: {e}")

        return resp.json()

    def build_url(self, endpoint: str) -> str:
        """
        Build the full URL for the API endpoint.

        Args:
            endpoint (str): The API endpoint to append to the base URL.

        Returns:
            str: The full URL for the API request.
        """
        return f"{self.base_url}/{endpoint}"

    def _prepare_headers(self, headers: dict = None):
        """
        Prepare headers for web request

        Adds Authorizaion headers if not present

        Returns:
            dict: Headers for the web request
        """
        if not headers:
            headers = {"Authorization": f"{self.auth.token['token_type']} {self.auth.access_token}"}
        else:
            if "Authorization" not in headers:
                headers["Authorization"] = f"{self.auth.token['token_type']} {self.auth.access_token}"
        return headers

    def _prepare_params(self, defaults: dict, params: dict) -> dict:
        """
        Prepare parameters for web request by merging defaults and provided parameters.

        Args:
            defaults (dict): Default parameters.
            params (dict): Provided parameters.

        Returns:
            dict: Final parameters for the GET request.
        """
        if not params:
            return defaults
        else:
            for key, value in defaults.items():
                if key not in params.keys():
                    params[key] = value
            return params

    def get_endpoints(
        self,
        query: dict = None,
        count: bool = False,
        params: dict = None,
        days: int = 3,
        kind: str = "*",
    ) -> dict:
        """
        Fetches all endpoints of a given kind from the registry api

        Args:
            query (dict):
                Query to send to the registry API, defaults agents reporting in the last 3 days
            days (int):
                Number of days to query for, defaults to 3
            kind (str):
                Type of agent to return,
                Accepts '*', 'agent:saas', or 'updater:saas', defaults to '*'
            count (bool):
                Return count of endpoints only
            params (dict):
                Custom query parameters to include in web request

        Returns:
            dict: A list of endpoint objects

        """
        range_query = {"range": {"event.observedAt": {"gte": f"now-{str(days)}d", "lt": "now"}}}
        must_query = [range_query]

        kind_query = {"match_phrase": {"component.kind": {"query": f"{kind}"}}}
        if kind == "agent:saas" or kind == "updater:saas":
            must_query.append(kind_query)

        unknown_version = {"match_phrase": {"component.version": {"query": "unknown"}}}
        unregistered_status = {"match_phrase": {"component.status.code": {"query": "it:component:status:unregistered"}}}
        picp_component = {"match_phrase": {"component.kind": {"query": "feeder:picp"}}}
        must_not_query = [unknown_version, unregistered_status, picp_component]

        if query is None:
            query = {"query": {"bool": {"must": must_query, "must_not": must_not_query}}}
        endpoints = self.registry_search(query, "component", params=params, stream=True)
        return endpoints

    def get_rules(self, includes: str = "*", headers: dict = None, params: dict = None) -> list:
        """
        Query for all rules in the depot API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict):
                headers to include in the http request, if not provided
                a default header will be created with auth info
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            list: A list of rules objects

        """
        endpoint = "ruler/rules"

        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp["data"]

    def get_rule(self, id_: str, includes: str = "*", headers: dict = None, params: dict = None) -> dict:
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
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            dict: A dict of rule attributes

        """
        endpoint = f"ruler/rules/{id_}"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def update_rule(self, id_: str, rule: Rule, headers: dict = None, test: bool = False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = f"ruler/rules/{id_}"
        data = rule.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.put(
            self.build_url(endpoint),
            headers=headers,
            json=data,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def create_rule(self, rule: Rule, headers: dict = None, test=False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = "ruler/rules"
        data = {"data": [rule.as_dict()]}

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=data,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def delete_rule(self, id_, headers: dict = None):
        """
        Delete a rule.

        Args:
            id_ (str): The ID of the object to delete.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f"ruler/rules/{id_}"
        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.delete(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_predicates(self, includes: str = "*", headers: dict = None, params: dict = None) -> list:
        """
        Query for all predicates in the depot API, does not return built-in

        Args:
            includes (str):
                Comma-separated list of attributes to include, default = *
            headers (dict):
                headers to include in the http request, if not
                a default header will be created with auth info
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            list: A list of predicate objects
        """
        endpoint = "depot/predicates"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp["data"]

    def get_predicate(self, id_: str, includes: str = "*", headers: dict = None, params: dict = None) -> dict:
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
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            dict: A dict of predicate attributes
        """
        endpoint = f"depot/predicates/{id_}"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def get_conditions(self, includes: str = "*", headers: dict = None, params: dict = None) -> list:
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
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            list: Returns list of predicate objects
        """
        endpoint = "depot/predicates"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        conditions = []
        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        for predicate in resp["data"]:
            if predicate["kind"] == "it:predicate:custom:match":
                conditions.append(predicate)
        return conditions

    def update_predicate(self, id_, predicate: Predicate, headers: dict = None, test: bool = False) -> dict:
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
        endpoint = f"depot/predicates/{id_}"
        data = predicate.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def overwrite_predicate(self, id_, predicate: Predicate, headers: dict = None, test: bool = False) -> dict:
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
        endpoint = f"depot/predicates/{id_}"
        data = predicate.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.put(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_predicate(self, predicate: Predicate, headers: dict = None, test: bool = False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = "depot/predicates"
        data = {"data": [predicate.as_dict()]}

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def delete_predicate(self, id_, headers: dict = None):
        """
        Delete a predicate.

        Args:
            id_ (str): The ID of the object to delete.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f"depot/predicates/{id_}"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.delete(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_tags(self, includes: str = "*", headers: dict = None, params: dict = None) -> list:
        """
        Query for all tags in the depot API, does not return built-in tags

        Args:
            includes (str): Comma-separated list of attributes to include, default is '*'.
            headers (dict): Headers to include in the HTTP request, if not provided, a default header
                will be created with auth info.
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            list: A list of tags objects.

        """
        endpoint = "depot/tags"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp["data"]

    def get_tag(self, id_: str, includes: str = "*", headers: dict = None, params: dict = None) -> dict:
        """
        Get tag by ID.

        Args:
            id_ (str): The tag ID.
            includes (str): Comma-separated list of attributes to include. Default is '*'.
            headers (dict): Headers to include in the HTTP request. If not provided, a default header
                will be created with auth info.
            params (dict):
                Custom query parameters to include in GET request

        Returns:
            dict: A dictionary of tag information.

        """
        endpoint = f"depot/tags/{id_}"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def update_tag(self, id_: str, tag: Tag, headers: dict = None, test: bool = False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = f"depot/tags/{id_}"
        data = tag.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_tag(self, tag: Tag, headers: dict = None, test: bool = False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = "depot/tags"
        data = tag.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def add_activity_tag(self, fqid, tag_id, headers: dict = None, params: dict = None) -> dict:
        """
        Add a tag to an activity.

        Parameters:
            fqid (str): The fully qualified ID of the activity to add the tag to.
            tag_id (str): The ID of the tag to be added.
            headers (dict, optional): Additional headers to include in the HTTP request.
                                    Defaults to an empty dictionary.
            params (dict):
                Custom query parameters to send with request

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f"activity/events/{fqid}/tags"
        defaults = {"tagValue": tag_id}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.patch(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def add_activity_assignee(self, fqid, admin_id, headers: dict = None) -> dict:
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
        endpoint = f"activity/events/{fqid}/annotations/workflow/assignment"
        data = {"id": admin_id}

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.put(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_agent_policies(self, includes: str = "*", headers: dict = None, params: dict = None) -> list:
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
        endpoint = "registry/policies"

        defaults = {"limit": 99, "offset": 0, "includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def get_agent_policy(self, id_: str, includes: str = "*", headers: dict = None, params: dict = None) -> dict:
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
        endpoint = f"registry/policies/{id_}"

        defaults = {"limit": 99, "offset": 0, "includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {
                "url": self.build_url(endpoint),
                "headers": headers,
                "params": params,
            }

        resp = self.session.get(
            self.build_url(endpoint),
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def update_agent_policy(self, id_, policy: AgentPolicy, headers: dict = None, test: bool = False) -> dict:
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
            return {"status": 200, "msg": "success"}

        endpoint = f"registry/policies/{id_}"
        data = policy.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def overwrite_agent_policy(self, id_, policy: AgentPolicy, headers: dict = None, test: bool = False) -> dict:
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
            return {"status": 200, "msg": "success"}

        endpoint = f"registry/policies/{id_}"
        data = policy.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.put(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_agent_policy(self, policy: AgentPolicy, headers: dict = None, test: bool = False) -> dict:
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
            return {"status": 200, "msg": "success"}

        endpoint = "registry/policies"
        data = policy.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_notification_policies(self, includes: str = "*", headers: dict = None, params: dict = {}) -> list:
        """
        Query for all notification policies in the notifications API

        Args:
            includes (str):
                comma-separated list of attributes to include, default = *
            headers (dict):
                headers to include in the http request, if not provided
                a default header will be created with auth info
            params (dict):
                Custom query parameters to include in request

        Returns:
            list: A list containing notification policies
        """
        endpoint = "notification/target-groups"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params}

        resp = self.session.get(self.build_url(endpoint), headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def update_notification_policy(
        self,
        id_: str,
        target_group: TargetGroup,
        headers: dict = None,
        test: bool = False,
    ) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = f"notification/target-groups/{id_}"
        data = target_group.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_notification_policy(self, target_group: TargetGroup, headers: dict = None, test: bool = False) -> dict:
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
            return {"id": str(uuid.uuid4())}

        endpoint = "notification/target-groups"
        data = [target_group.as_dict()]

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_dictionaries(self, headers: dict = None, includes: str = "*", params: dict = None) -> list:
        """
        Retrieve dictionaries from the API endpoint.

        Args:
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            includes (str, optional): A string specifying the entities to include in the response.
                Defaults to '*', which includes all entities.
            params (dict):
                Custom query parameters to include in request

        Returns:
            list: A list containing the retrieved dictionaries.

        """
        endpoint = "ruler/configurations/dlp/dictionaries"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params}

        resp = self.session.get(self.build_url(endpoint), headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_dictionary(self, id_: str, headers: dict = None, includes: str = None, params: dict = None) -> dict:
        """
        Retrieve a specific dictionary from the API endpoint.

        Args:
            id_ (str): The ID of the dictionary to retrieve.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            includes (str, optional): A string specifying the entities to include in the response.
                Defaults to None.
            params (dict):
                Custom query parameters to include in request

        Returns:
            dict: A dictionary containing the retrieved dictionary.

        """
        endpoint = f"ruler/configurations/dlp/dictionaries/{id_}"
        defaults = {"include": includes}  # include is different with this req
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params}

        resp = self.session.get(self.build_url(endpoint), headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_dictionary_terms(self, id_: str, headers: dict = None, includes: str = "*", params: dict = None) -> list:
        """
        Retrieve terms from a specific dictionary in the API endpoint.

        Args:
            id_ (str): The ID of the dictionary to retrieve terms from.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.
            includes (str, optional): A string specifying the entities to include in the response.
                Defaults to '*', which includes all entities.
            params (dict):
                Custom query parameters to include in request

        Returns:
            list: A list containing the retrieved terms.

        """
        endpoint = f"ruler/configurations/dlp/dictionaries/{id_}/entries"
        defaults = {"includes": includes}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params}

        resp = self.session.get(self.build_url(endpoint), headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def update_dictionary(self, id_: str, dictionary: Dictionary, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/dictionaries/{id_}"
        data = dictionary.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_dictionary(self, dictionary: Dictionary, headers: dict = None) -> dict:
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
        endpoint = "ruler/configurations/dlp/dictionaries"
        data = dictionary.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_dictionaries(self, dictionaries: list[Dictionary], headers: dict = None) -> list:
        """
        Creates or updates a batch list of dictionaries

        Args:
            dictionaries (list): A list of proofpoint_itm.classes.Dictionary objects
            headers (dict): Headers to include in the http request, if not provided
                a default header will be created with auth info

        Returns:
            list: A list containing the created dictionaries.
        """
        endpoint = "ruler/configurations/dlp/dictionaries"
        data = {"data": [d.as_dict() for d in dictionaries]}

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def delete_dictionary(self, id_: str, headers: dict = None) -> dict:
        """
        Delete a dictionary.

        Args:
            id_ (str): The ID of the dictionary to delete.
            headers (dict, optional): Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = f"ruler/configurations/dlp/dictionaries/{id_}"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.delete(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def update_event_workflow(self, fqid: str, status: str, headers: dict = None) -> dict:
        """Update workflow status of an alert/incident

        Args:
            fqid_ (str): The fqid of an event/incident
            status (str): The new status to be applied to the incident
                Accepts new, reopened, in-progress, escalated, on-hold,
                resolved, false-positive, not-an-issue

        Returns:
            dict: A dictionary containing the API response.
        """
        endpoint = f"activity/events/{fqid}/annotations/workflow"
        data = {"state": {"status": f"incident:status:{status}"}}

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_detectors(self, headers: dict = None) -> list:
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
        endpoint = "ruler/configurations/dlp/detectors"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.get(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_detector(self, id_: str, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/detectors/{id_}"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.get(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def update_detector(self, id_: str, detector: Detector, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/detectors/{id_}"
        data = detector.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_detector(self, detector: Detector, headers: dict = None) -> dict:
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
        endpoint = "ruler/configurations/dlp/detectors"
        data = detector.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_detector_sets(self, headers: dict = None) -> list:
        """
        Retrieve detector sets from the API endpoint.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            list: A list containing the retrieved detector sets.

        """
        endpoint = "ruler/configurations/dlp/detectorsets"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.get(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_detector_set(self, id_: str, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/detectorsets/{id_}"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.get(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def update_detector_set(self, id_: str, detector_set: DetectorSet, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/detectorsets/{id_}"
        data = detector_set.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.patch(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def create_detector_set(self, detector_set: DetectorSet, headers: dict = None) -> dict:
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
        endpoint = "ruler/configurations/dlp/detectorsets"
        data = detector_set.as_dict()

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.post(self.build_url(endpoint), headers=headers, json=data, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def delete_detector_set(self, id_: str, headers: dict = None) -> dict:
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
        endpoint = f"ruler/configurations/dlp/detectorsets/{id_}"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.delete(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def get_smartids(self, headers: dict = None) -> list:
        """
        Retrieve smart IDs from the API endpoint.

        Args:
            headers (dict, optional):
                Additional headers to include in the HTTP request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the retrieved smart IDs.

        """
        endpoint = "ruler/configurations/dlp/smartids"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": None}

        resp = self.session.get(self.build_url(endpoint), headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        return resp.json()

    def publish_config(self, headers: dict = None, artifactID: str = "activity", data: dict = None) -> dict:
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
        endpoint = f"ruler/artifacts/{artifactID}"
        data = {} if data is None else data

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "body": data}

        resp = self.session.put(self.build_url(endpoint), headers=headers, json=data)
        return resp.json()

    def depot_search(self, query: dict, entity: str, params: dict = None, headers: dict = None) -> dict:
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
        endpoint = "depot/queries"
        defaults = {"entityTypes": entity}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params, "body": query}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=query,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def notification_search(self, query: dict, entity: str, params: dict = None, headers: dict = None) -> dict:
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
        endpoint = "notification/queries"
        defaults = {"entityTypes": entity}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params, "body": query}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=query,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def ruler_search(self, query: str, entity: str, params: dict = None, headers: dict = None) -> dict:
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
        endpoint = "ruler/queries"
        defaults = {"entityTypes": entity}
        params = self._prepare_params(defaults, params)

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params, "body": query}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=query,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def activity_search(
        self,
        query: dict,
        entity: str,
        params: dict = None,
        headers: dict = None,
        stream: bool = False,
    ) -> dict:
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
            stream (bool):
                Flag to invoke the streaming response

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = "/v2/apis/activity/event-queries"
        defaults = {"entityTypes": entity}
        params = self._prepare_params(defaults, params)
        if stream:
            if not headers:
                headers = {"Accept": "application/jsonl"}
            else:
                headers["Accept"] = "application/jsonl"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params, "body": query}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=query,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()

    def registry_search(
        self,
        query: dict,
        entity: str,
        params: dict = None,
        headers: dict = None,
        stream: bool = False,
    ) -> dict:
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
            stream (bool):
                Flag to invoke the streaming response

        Returns:
            dict: A dictionary containing the API response.

        """
        endpoint = "registry/queries"
        defaults = {"entityTypes": entity}
        params = self._prepare_params(defaults, params)
        if stream:
            if not headers:
                headers = {"Accept": "application/jsonl"}
            else:
                headers["Accept"] = "application/jsonl"

        if self.development_mode:
            return {"url": self.build_url(endpoint), "headers": headers, "params": params, "body": query}

        resp = self.session.post(
            self.build_url(endpoint),
            headers=headers,
            json=query,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return resp.json()
