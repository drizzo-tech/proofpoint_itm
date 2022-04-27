# proofpoint_itm
Proofpoint ITM API client library for python

## Installation
```
python -m pip install proofpoint_itm
```

## Usage

Create a front end script to import the ITMClient class and create a new ITMClient object by passing in the ITM Console URL, API Client ID, and either a client secret or username and password.

```python
from proofpoint_itm import ITMClient

itm_client = ITMClient(
    <itm console url>,
    <api client id>,
    <api client secret>)
```


