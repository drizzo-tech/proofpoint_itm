"""
Tests for ITMClient search methods.
"""
import pytest
import responses
from unittest.mock import Mock


class TestDepotSearch:
    """Test depot_search method."""
    
    @responses.activate
    def test_depot_search_success(self, mock_client, sample_search_query):
        """Test successful depot search."""
        url = f"{mock_client.base_url}/depot/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "result-1"}]},
            status=200
        )
        
        result = mock_client.depot_search(sample_search_query, "predicate")
        
        assert "data" in result
        assert len(result["data"]) == 1
        assert "entityTypes=predicate" in responses.calls[0].request.url
    
    @responses.activate
    def test_depot_search_with_params(self, mock_client, sample_search_query):
        """Test depot search with custom parameters."""
        url = f"{mock_client.base_url}/depot/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": []},
            status=200
        )
        
        params = {"offset": 10, "limit": 50}
        result = mock_client.depot_search(sample_search_query, "tag", params=params)
        
        request_url = responses.calls[0].request.url
        assert "offset=10" in request_url
        assert "limit=50" in request_url
    
    def test_depot_search_development_mode(self, development_client, sample_search_query):
        """Test depot search in development mode."""
        result = development_client.depot_search(sample_search_query, "predicate")
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
        assert result["body"] == sample_search_query


class TestNotificationSearch:
    """Test notification_search method."""
    
    @responses.activate
    def test_notification_search_success(self, mock_client, sample_search_query):
        """Test successful notification search."""
        url = f"{mock_client.base_url}/notification/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "notification-1"}]},
            status=200
        )
        
        result = mock_client.notification_search(sample_search_query, "target-group")
        
        assert "data" in result
        assert "entityTypes=target-group" in responses.calls[0].request.url


class TestRulerSearch:
    """Test ruler_search method."""
    
    @responses.activate
    def test_ruler_search_success(self, mock_client, sample_search_query):
        """Test successful ruler search."""
        url = f"{mock_client.base_url}/ruler/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "rule-1"}]},
            status=200
        )
        
        result = mock_client.ruler_search(sample_search_query, "rule")
        
        assert "data" in result
        assert "entityTypes=rule" in responses.calls[0].request.url


class TestActivitySearch:
    """Test activity_search method."""
    
    @responses.activate
    def test_activity_search_success(self, mock_client, sample_search_query):
        """Test successful activity search."""
        url = f"{mock_client.base_url}/activity/event-queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "event-1"}]},
            status=200
        )
        
        result = mock_client.activity_search(sample_search_query, "event")
        
        assert "data" in result
    
    @responses.activate
    def test_activity_search_streaming(self, mock_client, sample_search_query):
        """Test activity search with streaming enabled."""
        url = f"{mock_client.base_url}/activity/event-queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "event-1"}]},
            status=200
        )
        
        result = mock_client.activity_search(sample_search_query, "event", stream=True)
        
        # Check that Accept header was set for streaming
        assert responses.calls[0].request.headers.get("Accept") == "application/jsonl"


class TestRegistrySearch:
    """Test registry_search method."""
    
    @responses.activate
    def test_registry_search_success(self, mock_client, sample_search_query):
        """Test successful registry search."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "component-1"}]},
            status=200
        )
        
        result = mock_client.registry_search(sample_search_query, "component")
        
        assert "data" in result
    
    @responses.activate
    def test_registry_search_streaming(self, mock_client, sample_search_query):
        """Test registry search with streaming enabled."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": []},
            status=200
        )
        
        headers = {"Custom-Header": "value"}
        result = mock_client.registry_search(
            sample_search_query, 
            "component", 
            headers=headers,
            stream=True
        )
        
        # Check that Accept header was added to existing headers
        assert responses.calls[0].request.headers.get("Accept") == "application/jsonl"
        assert responses.calls[0].request.headers.get("Custom-Header") == "value"


class TestGetEndpoints:
    """Test get_endpoints method (uses registry_search)."""
    
    @responses.activate
    def test_get_endpoints_default_query(self, mock_client):
        """Test get_endpoints with default query."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [{"id": "endpoint-1"}]},
            status=200
        )
        
        result = mock_client.get_endpoints()
        
        assert "data" in result
        # Verify the query was constructed with default parameters
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_get_endpoints_with_kind_filter(self, mock_client):
        """Test get_endpoints with specific kind filter."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": []},
            status=200
        )
        
        result = mock_client.get_endpoints(kind="agent:saas")
        
        # Verify the request was made
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_get_endpoints_custom_days(self, mock_client):
        """Test get_endpoints with custom days parameter."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": []},
            status=200
        )
        
        result = mock_client.get_endpoints(days=7)
        
        assert len(responses.calls) == 1
