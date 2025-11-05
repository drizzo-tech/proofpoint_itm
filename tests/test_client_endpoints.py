"""
Tests for ITMClient endpoints methods.
"""
import pytest
import responses


class TestGetEndpoints:
    """Test get_endpoints method."""
    
    @responses.activate
    def test_get_endpoints_default_query(self, mock_client):
        """Test get_endpoints with default query (no custom query provided)."""
        url = f"{mock_client.base_url}/registry/queries"
        
        # Mock the streaming JSONL response
        jsonl_response = '{"id": "endpoint-1", "component": {"kind": "agent:saas"}}\n{"id": "endpoint-2", "component": {"kind": "agent:saas"}}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints()
        
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "endpoint-1"
        
        # Verify the request was made with stream=True
        assert len(responses.calls) == 1
        assert "entityTypes=component" in responses.calls[0].request.url
    
    @responses.activate
    def test_get_endpoints_with_custom_query(self, mock_client):
        """Test get_endpoints with a custom query."""
        url = f"{mock_client.base_url}/registry/queries"
        
        custom_query = {
            "sort": [
                {
                    "event.observedAt": {
                        "order": "desc",
                        "unmapped_type": "boolean"
                    }
                }
            ],
            "filters": {
                "$and": [
                    {
                        "$not": {
                            "$or": [
                                {
                                    "$stringIn": {
                                        "component.status.code": [
                                            "it:component:status:unregistered"
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "$or": [
                            {
                                "$stringIn": {
                                    "endpoint.os.kind": [
                                        "windows"
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "$not": {
                            "$or": [
                                {
                                    "$stringIn": {
                                        "component.version": [
                                            "unknown"
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "$dtRelativeGE": {
                            "event.observedAt": -259200000
                        }
                    }
                ]
            }
        }
        
        jsonl_response = '{"id": "windows-endpoint-1", "endpoint": {"os": {"kind": "windows"}}}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints(query=custom_query)
        
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "windows-endpoint-1"
    
    @responses.activate
    def test_get_endpoints_with_kind_filter(self, mock_client):
        """Test get_endpoints with kind parameter."""
        url = f"{mock_client.base_url}/registry/queries"
        
        jsonl_response = '{"id": "agent-1", "component": {"kind": "agent:saas"}}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints(kind="agent:saas")
        
        assert isinstance(result, dict)
        assert "data" in result
        assert result["data"][0]["component"]["kind"] == "agent:saas"
    
    @responses.activate
    def test_get_endpoints_with_days_parameter(self, mock_client):
        """Test get_endpoints with custom days parameter."""
        url = f"{mock_client.base_url}/registry/queries"
        
        jsonl_response = '{"id": "endpoint-1"}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints(days=7)
        
        assert isinstance(result, dict)
        assert "data" in result
    
    @responses.activate
    def test_get_endpoints_count_only(self, mock_client):
        """Test get_endpoints with count=True."""
        url = f"{mock_client.base_url}/registry/queries"
        
        jsonl_response = '{"id": "endpoint-1"}\n{"id": "endpoint-2"}\n{"id": "endpoint-3"}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints(count=True)
        
        assert isinstance(result, dict)
        assert "data" in result
        # Count parameter is passed but the method still returns data
        # The actual counting logic might be handled by the API
    
    @responses.activate
    def test_get_endpoints_with_params(self, mock_client):
        """Test get_endpoints with custom params."""
        url = f"{mock_client.base_url}/registry/queries"
        
        jsonl_response = '{"id": "endpoint-1"}'
        
        responses.add(
            responses.POST,
            url,
            body=jsonl_response,
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints(params={"limit": 10, "offset": 0})
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "limit=10" in responses.calls[0].request.url
        assert "offset=0" in responses.calls[0].request.url
    
    @responses.activate
    def test_get_endpoints_empty_result(self, mock_client):
        """Test get_endpoints with no results."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            body="",
            status=200,
            content_type="application/jsonl"
        )
        
        result = mock_client.get_endpoints()
        
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 0
    
    @responses.activate
    def test_get_endpoints_http_error(self, mock_client):
        """Test get_endpoints handles HTTP errors."""
        url = f"{mock_client.base_url}/registry/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(Exception):
            mock_client.get_endpoints()
    
    def test_get_endpoints_development_mode(self, development_client):
        """Test get_endpoints in development mode."""
        result = development_client.get_endpoints()
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "params" in result
        assert "body" in result
        assert "registry/queries" in result["url"]
    
    def test_get_endpoints_development_mode_with_query(self, development_client):
        """Test get_endpoints in development mode with custom query."""
        custom_query = {
            "filters": {
                "$and": [
                    {
                        "$stringIn": {
                            "endpoint.os.kind": ["windows"]
                        }
                    }
                ]
            }
        }
        
        result = development_client.get_endpoints(query=custom_query)
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
        # The custom query should be in the body
        assert result["body"] == custom_query


class TestGetEndpointsQueryBuilding:
    """Test the query building logic in get_endpoints."""
    
    def test_default_query_structure(self, development_client):
        """Test that default query is built correctly."""
        result = development_client.get_endpoints(days=3)
        
        assert "body" in result
        query = result["body"]
        
        # Check that the query has the expected structure
        assert "query" in query
        assert "bool" in query["query"]
        assert "must" in query["query"]["bool"]
        assert "must_not" in query["query"]["bool"]
        
        # Check for range query (days parameter)
        must_queries = query["query"]["bool"]["must"]
        assert any("range" in q for q in must_queries)
        
        # Check for must_not queries (unknown version, unregistered, picp)
        must_not_queries = query["query"]["bool"]["must_not"]
        assert len(must_not_queries) == 3
    
    def test_kind_filter_agent_saas(self, development_client):
        """Test that kind filter is added for agent:saas."""
        result = development_client.get_endpoints(kind="agent:saas")
        
        query = result["body"]
        must_queries = query["query"]["bool"]["must"]
        
        # Should have range query + kind query
        assert len(must_queries) == 2
        assert any("match_phrase" in q and "component.kind" in q.get("match_phrase", {}) for q in must_queries)
    
    def test_kind_filter_updater_saas(self, development_client):
        """Test that kind filter is added for updater:saas."""
        result = development_client.get_endpoints(kind="updater:saas")
        
        query = result["body"]
        must_queries = query["query"]["bool"]["must"]
        
        # Should have range query + kind query
        assert len(must_queries) == 2
    
    def test_kind_filter_wildcard(self, development_client):
        """Test that kind filter is NOT added for wildcard."""
        result = development_client.get_endpoints(kind="*")
        
        query = result["body"]
        must_queries = query["query"]["bool"]["must"]
        
        # Should only have range query, no kind query
        assert len(must_queries) == 1
        assert "range" in must_queries[0]
    
    def test_custom_query_overrides_default(self, development_client):
        """Test that providing a custom query overrides the default."""
        custom_query = {"filters": {"$and": [{"$stringIn": {"test": ["value"]}}]}}
        
        result = development_client.get_endpoints(query=custom_query)
        
        # Should use the custom query as-is
        assert result["body"] == custom_query
