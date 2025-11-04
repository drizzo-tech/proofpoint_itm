"""
Tests for ITMClient error handling.
"""
import pytest
import responses
from requests.exceptions import Timeout, ConnectionError, HTTPError


class TestHTTPErrors:
    """Test HTTP error handling."""
    
    @responses.activate
    def test_404_not_found(self, mock_client):
        """Test handling of 404 Not Found errors."""
        url = f"{mock_client.base_url}/ruler/rules/nonexistent"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Not found"},
            status=404
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rule("nonexistent")
    
    @responses.activate
    def test_400_bad_request(self, mock_client):
        """Test handling of 400 Bad Request errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Bad request"},
            status=400
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rules()
    
    @responses.activate
    def test_401_unauthorized(self, mock_client):
        """Test handling of 401 Unauthorized errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Unauthorized"},
            status=401
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rules()
    
    @responses.activate
    def test_403_forbidden(self, mock_client):
        """Test handling of 403 Forbidden errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Forbidden"},
            status=403
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rules()
    
    @responses.activate
    def test_500_internal_server_error(self, mock_client):
        """Test handling of 500 Internal Server Error."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rules()
    
    @responses.activate
    def test_503_service_unavailable(self, mock_client):
        """Test handling of 503 Service Unavailable."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Service unavailable"},
            status=503
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rules()


class TestNetworkErrors:
    """Test network error handling."""
    
    @responses.activate
    def test_timeout_error(self, mock_client):
        """Test handling of timeout errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            body=Timeout("Request timed out")
        )
        
        with pytest.raises(Timeout):
            mock_client.get_rules()
    
    @responses.activate
    def test_connection_error(self, mock_client):
        """Test handling of connection errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            body=ConnectionError("Connection failed")
        )
        
        with pytest.raises(ConnectionError):
            mock_client.get_rules()


class TestResponseParsing:
    """Test response parsing edge cases."""
    
    @responses.activate
    def test_malformed_json_response(self, mock_client):
        """Test handling of malformed JSON responses."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            body="This is not JSON",
            status=200,
            content_type="application/json"
        )
        
        with pytest.raises(Exception):
            mock_client.get_rules()
    
    @responses.activate
    def test_missing_data_key(self, mock_client):
        """Test handling when expected 'data' key is missing."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"results": []},  # Wrong key
            status=200
        )
        
        with pytest.raises(KeyError):
            mock_client.get_rules()
    
    @responses.activate
    def test_null_response_data(self, mock_client):
        """Test handling of null data in response."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"data": None},
            status=200
        )
        
        # get_rules returns resp.json()["data"] which would be None
        # This actually returns None, not an error - the client doesn't validate
        result = mock_client.get_rules()
        assert result is None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @responses.activate
    def test_empty_string_id(self, mock_client):
        """Test methods with empty string ID."""
        url = f"{mock_client.base_url}/ruler/rules/"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Invalid ID"},
            status=400
        )
        
        with pytest.raises(HTTPError):
            mock_client.get_rule("")
    
    @responses.activate
    def test_special_characters_in_id(self, mock_client):
        """Test methods with special characters in ID."""
        special_id = "rule-123!@#$%"
        url = f"{mock_client.base_url}/ruler/rules/{special_id}"
        
        responses.add(
            responses.GET,
            url,
            json={"id": special_id},
            status=200
        )
        
        result = mock_client.get_rule(special_id)
        assert result["id"] == special_id
    
    def test_none_parameters(self, mock_client):
        """Test methods handle None parameters gracefully."""
        # Should not raise errors with None params
        result = mock_client._prepare_params({"default": "value"}, None)
        assert result["default"] == "value"
