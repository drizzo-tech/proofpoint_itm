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

## Documentation

General documentation can be found here: [proofpoint_itm documentation](https://proofpoint-itm.readthedocs.io/en/latest/index.html)

Detailed API reference documentation here: [API Reference](https://proofpoint-itm.readthedocs.io/en/latest/api.html)
