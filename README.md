# proofpoint_itm
Proofpoint ITM API client library for python

## Installation
```
python -m pip install proofpoint_itm
```

## Usage

Create a front end script to import the ITMClient class and create a new ITMClient object by passing in the tenant ID (first part of the admin console url), API Client ID, and client secret as a dict.

```python
from proofpoint_itm import ITMClient

itm_client = ITMClient(
    {
        'tenant_id': <tenant id>,
        'client_id': <api client id>,
        'client_secret': <api client secret>
    }
)
```

## Get Requests
** Not all API objects are supported for get requests, additional API gets will be updated as needed

This library supports get requests for the following object types:
- Endpoints
- Rules
- Predicates (Conditions)
- Tags
- Agent Policies
- Notification Policies
- Dictionaries
- Dictionary Terms
- Detectors
- Detector Sets
- Smart IDs

Get requests return a python dictionary object with the corresponding object attributes or a list of objects. See examples below

---

### Endpoints
```
endpoints = itm_client.get_endpoints()
```

>### get_endpoints: (includes: str = '\*', kind: str = '\*', status: str = '\*', headers: dict = None, count: bool = False) -> list
Gets endpoints from the registry API

Args:
* includes (str):
  * List of attributes to return, defaults to *
* kind (str):
  * Type of agent to return, Accepts *, agent:saas, or updater:saas, defaults to *
* status (str):
  * Filter by agent status. Accepts: *, HEALTHY, UNHEALTHY, UNREACHABLE, DEAD, INACTIVE

Returns:
* A list of endpoint objects

---

### Rules
```
rules = itm_client.get_rules()
rule = itm_client.get_rule(<id>)
```

>### get_rules: (includes: str = '\*', headers: dict = None) -> list
Query for all rules in the depot API

Args:
* includes (str):
  * comma-separated list of attributes to include, default = \*
* headers (dict): 
  * headers to include in the http request, if not provided a default header will be created with auth info

Returns: 
* A list of rule objects

>### get_rule: (id: str, includes: str = '\*', headers: dict = None) -> dict
Query for single rule by ID in the depot API

Args:
* id (str):
  * Rule id to return, if not provided, return all
* includes (str):
  * Comma-separated list of attributes to include, default = \*
* headers (dict): 
  * Headers to include in the http request, if not provided a default header will be created with auth info

Returns: 
* A dict of rule attributes

---

### Predicates (Conditions)
```
predicates = itm_client.get_predicates()
predicate = itm_client.get_predicate(<id>)
```
Predicates are conditions either configured directly in a rule, or created as a standalone 'condition'

>### get_predicates: (includes: str = '\*', headers: dict = None) -> list
Query for all predicates in the depot API, does not return built-in/global predicates but will return rule predicates in addition to condition predicates.

Args:
* includes (str): 
  * Comma-separated list of attributes to include, default = \*
* headers (dict): 
  * headers to include in the http request, if not provided a default header will be created with auth info

Returns: 
* A list of predicates objects

>### get_predicate: (id: str, includes: str = '*', headers: dict = None) -> dict
Query for a single predicate by ID

Args:
* id (str):
  * The predicate id to return
* includes (str): 
  * Comma-separated list of attributes to include, default = \*
* headers (dict): 
  * headers to include in the http request, if not provided a default header will be created with auth info

Returns:
* A dict of predicate attributes

>### get_conditions: (includes: str = '\*', headers: dict = None) -> list 
Query for all custom conditions (user created) that are not auto created from rules. This is the condition list defined in Definitions > Conditions in the admin GUI.

Uses the get_predicates call, then post filters for kind = it:predicate:custom:match

Args:
* includes (str): 
  * comma-separated list of attributes to include, default = \*
* headers (dict): 
  * headers to include in the http request, if not provided a default header will be created with auth info

Returns:
* Returns list of predicate objects

---

### Searches
* activity_search
* depot_search
* noficiation_search
* registry_search
* ruler_search

Searches require a query be provided as a dictionary representing an elasitcsearch query.

This is a simple example, more information can be found here: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
```
{
  "query": {
    "bool": {
      "filter": {
        "term": {
          "status": "active"
        }
      }
    }
  }
}

```

Aggregate searches are also supported
```
{
  "aggs": {
    "my-agg-name": {
      "terms": {
        "field": "my-field"
      }
    }
  }
}
```

### activity_search(query: dict, entity: str, params: dict = None, headers: dict = None)
Performs a search query against the activity API


* **Parameters**

    
    * **query** (*dict*) – A dict representing an Elasticsearch query, will be converted to json string


    * **entity** (*str*) – entityTypes to search for
    Accepted values: event, casbevent, audit, network


    * **params** (*dict*) – A dict of web request url parameters
    ex. offset = 0, limit=500


    * **headers** (*dict*) – Headers to include in the http request, if not provided
    a default header will be created with auth info

* **Returns**

    urllib.response object (dict)

### depot_search(query: str, entity: str, params: dict = None, headers: dict = None)
Performs a search query against the depot API


* **Parameters**

    
    * **query** (*dict*) – A dict representing an Elasticsearch query, will be converted to json string


    * **entity** (*str*) – entityTypes to search for
    Accepted values: list, predicate, tag, article


    * **params** (*dict*) – A dict of web request url parameters
    ex. offset=0, limit=500


    * **headers** (*dict*) – Headers to include in the http request, if not provided
    a default header will be created with auth info



* **Returns**

    dict of returned objects

### notification_search(query: dict, entity: str, params: dict = None, headers: dict = None)
Performs a search query against the notification API


* **Parameters**

    
    * **query** (*dict*) – A dict representing an Elasticsearch query, will be converted to json string


    * **entity** (*str*) – entityTypes to search for
    Accepted values: target-group, notification


    * **params** (*dict*) – A dict of web request url parameters
    ex. offset=0, limit=500


    * **headers** (*dict*) – Headers to include in the http request, if not provided
    a default header will be created with auth info



* **Returns**

    dict of returned objects

### registry_search(query: dict, entity: str, params: Optional[dict] = None, headers: Optional[dict] = None)
Performs a search query against the registry API


* **Parameters**

    
    * **query** (*dict*) – A dict representing an Elasticsearch query, will be converted to json string


    * **entity** (*str*) – entityTypes to search for
    Accepted values: component, component-change, endpoint, endpoint-change, heartbeat


    * **params** (*dict*) – A dict of web request url parameters
    ex. offset=0, limit=500


    * **headers** (*dict*) – Headers to include in the http request, if not provided
    a default header will be created with auth info



* **Returns**

    urllib.response object (dict)

### ruler_search(query: str, entity: str, params: dict = None, headers: dict = None)
Performs a search query against the ruler API


* **Parameters**

    
    * **query** (*dict*) – A dict representing an Elasticsearch query, will be converted to json string


    * **entity** (*str*) – entityTypes to search for
    Accepted values: artifact, rule, rulechain


    * **params** (*dict*) – A dict of web request url parameters
    ex. offset=0, limit=500


    * **headers** (*dict*) – Headers to include in the http request, if not provided
    a default header will be created with auth info



* **Returns**

    dict of returned objects