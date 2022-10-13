from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

def get_request(url, headers=None, params=None, timeout=10):
    """
    Performs a get request
    params = dictionary of parameters to be added to the end of url
    headers = dictionary of headers to include in the request

    Returns response as dict
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    resp = make_request(url, headers=headers, method='GET')
    return resp


def post_request(url, headers=None, data=None, json_data=None, method='POST', params={}, timeout=10):
    """
    perform a post request
    pass headers/data as standard python dictionary
    use json_data instead of data if json encoded POST/PUT/PATCH
    override method with PUT or PATCH if desired

    Returns response as dict
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    if json_data:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(json_data)
        data = data.encode('utf-8')
    else:
        data = urlencode(data)
        data = data.encode('utf-8')

    resp = make_request(url, headers=headers, data=data, method=method)
    return resp

def delete_request(url, headers=None, params=None, timeout=10):
    """
    Performs a delete request
    params = dictionary of parameters to be added to the end of url
    headers = dictionary of headers to include in the request

    Returns response as dict
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    resp = make_request(url, headers=headers, method='DELETE')
    return resp

def make_request(url, headers=None, data=None, method=None, timeout=10):
    """
    creates and submits the request

    returns response as dict
    """
    request = Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return json.loads(body)
    except HTTPError as error:
        print(error.status, error.reason)
        body = error.read().decode()
        print(json.loads(body))
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")