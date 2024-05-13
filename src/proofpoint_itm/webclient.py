from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

def get_request(url, headers: dict=None, params: dict=None, stream: bool=False, timeout=10):
    """
    Performs a GET request to a given URL.

    Args:
        url (str): 
            The URL to which the GET request is made.
        headers (dict, optional): 
            Dictionary of headers to include in the request. Defaults to None.
        params (dict, optional): 
            Dictionary of parameters to be added to the end of the URL. Defaults to None.
        stream (bool, optional): 
            Boolean to indicate if the response should be streamed. Defaults to False.
        timeout (int, optional): 
            Maximum time to wait for a response. Defaults to 10.

    Returns:
        dict: Response from the request.
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    resp = make_request(url, headers=headers, method='GET', timeout=timeout)
    return resp


def post_request(url, headers=None, data=None, json_data=None, method='POST', params={}, stream=False ,timeout=10):
    """
    Performs a POST request to a given URL.

    Args:
        url (str): 
            The URL to which the POST request is made.
        headers (dict, optional): 
            Dictionary of headers to include in the request. Defaults to None.
        data (dict, optional): 
            Data to be sent in the body of the request. Defaults to None.
        json_data (dict, optional): 
            JSON-encoded data to be sent in the body of the request. Use this if sending JSON. Defaults to None.
        method (str, optional): 
            The HTTP method to be used. Can be overridden to 'PUT' or 'PATCH'. Defaults to 'POST'.
        params (dict, optional): 
            Dictionary of parameters to be added to the end of the URL. Defaults to an empty dictionary.
        stream (bool, optional): 
            Boolean to indicate if the response should be streamed. Defaults to False.
        timeout (int, optional): 
            Maximum time to wait for a response. Defaults to 10.

    Returns:
        dict: Response from the request.
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    if json_data is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        data = json.dumps(json_data)
        data = data.encode('utf-8')
    elif data:
        data = urlencode(data)
        data = data.encode('utf-8')

    if stream == True:
        headers['Accept'] = 'application/jsonl'

    resp = make_request(url, headers=headers, data=data, method=method, timeout=timeout, stream=stream)
    return resp

def delete_request(url, headers=None, params=None, timeout=10):
    """
    Performs a DELETE request to a given URL.

    Args:
        url (str): 
            The URL to which the DELETE request is made.
        headers (dict, optional): 
            Dictionary of headers to include in the request. Defaults to None.
        params (dict, optional): 
            Dictionary of parameters to be added to the end of the URL. Defaults to None.
        timeout (int, optional): 
            Maximum time to wait for a response. Defaults to 10.

    Returns:
        dict: Response from the request.
    """
    if params:
        url_params = urlencode(params)
        url = url + '?' + url_params

    resp = make_request(url, headers=headers, method='DELETE', timeout=timeout)
    return resp

def make_request(url, headers=None, data=None, method=None, stream=False, timeout=10):
    """
    Creates and submits the request based on the provided parameters.

    Args:
        url (str): 
            The URL to which the request is made.
        headers (dict, optional): 
            Dictionary of headers to include in the request. Defaults to None.
        data (dict or bytes, optional): 
            Data to be sent in the body of the request. Defaults to None.
        method (str, optional): 
            The HTTP method to be used. Defaults to None.
        stream (bool, optional): 
            Boolean to indicate if the response should be streamed. Defaults to False.
        timeout (int, optional): 
            Maximum time to wait for a response. Defaults to 10.

    Returns:
        dict: Response from the request.
    """
    
    request = Request(url, headers=headers or {}, data=data, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            if stream:
                return [json.loads(line) for line in response.readlines()]
            else:
                return json.loads(response.read())
    except HTTPError as error:
        print(error.status, error.reason)
        print(json.loads(error.read().decode()))
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")
