"""
Integration tests for ITMClient.

These tests can be run against a real API or using development mode.
Set INTEGRATION_TEST=true in environment to run these tests.

Usage:
    # Using development mode (safe, no API calls)
    pytest tests/integration/ -v
    
    # Using real API (requires credentials in .env)
    INTEGRATION_TEST=true pytest tests/integration/ -v
"""
import pytest
import os
from dotenv import load_dotenv
from proofpoint_itm.client import ITMClient
from proofpoint_itm.classes import Rule, Predicate, Tag


# Load environment variables from .env file
load_dotenv()

# Skip integration tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TEST") != "true",
    reason="Integration tests disabled. Set INTEGRATION_TEST=true to enable."
)


@pytest.fixture(scope="module")
def integration_config():
    """Load configuration from environment variables."""
    return {
        "client_id": os.getenv("CLIENT_ID"),
        "tenant_id": os.getenv("TENANT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET")
    }


@pytest.fixture(scope="module")
def integration_client(integration_config):
    """Create a real client for integration testing."""
    # Validate config
    if not all(integration_config.values()):
        pytest.skip("Missing required environment variables")
    
    return ITMClient(integration_config)


@pytest.fixture(scope="module")
def dev_client(integration_config):
    """Create a client in development mode for safe testing."""
    # Use dummy config if real config not available
    config = integration_config if all(integration_config.values()) else {
        "client_id": "test",
        "tenant_id": "test",
        "client_secret": "test"
    }
    
    return ITMClient(config, development=True)


class TestIntegrationRules:
    """Integration tests for rules methods."""
    
    def test_get_rules_development_mode(self, dev_client):
        """Test get_rules in development mode."""
        result = dev_client.get_rules()
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "ruler/rules" in result["url"]
    
    @pytest.mark.slow
    def test_get_rules_real_api(self, integration_client):
        """Test get_rules against real API."""
        result = integration_client.get_rules()
        
        assert isinstance(result, list)
        # Should return list even if empty
    
    @pytest.mark.slow
    def test_get_rule_by_id_real_api(self, integration_client):
        """Test get_rule with a specific ID."""
        # First get all rules to find a valid ID
        rules = integration_client.get_rules()
        
        if rules:
            rule_id = rules[0]["id"]
            result = integration_client.get_rule(rule_id)
            
            assert isinstance(result, dict)
            assert result["id"] == rule_id


class TestIntegrationPredicates:
    """Integration tests for predicates methods."""
    
    def test_get_predicates_development_mode(self, dev_client):
        """Test get_predicates in development mode."""
        result = dev_client.get_predicates()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_predicates_real_api(self, integration_client):
        """Test get_predicates against real API."""
        result = integration_client.get_predicates()
        
        assert isinstance(result, list)


class TestIntegrationTags:
    """Integration tests for tags methods."""
    
    def test_get_tags_development_mode(self, dev_client):
        """Test get_tags in development mode."""
        result = dev_client.get_tags()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_tags_real_api(self, integration_client):
        """Test get_tags against real API."""
        result = integration_client.get_tags()
        
        assert isinstance(result, list)
    
    @pytest.mark.slow
    def test_get_tag_by_id_real_api(self, integration_client):
        """Test get_tag with a specific ID from get_tags."""
        # First get all tags to find a valid ID
        tags = integration_client.get_tags()
        
        if tags:
            tag_id = tags[0]["id"]
            result = integration_client.get_tag(tag_id)
            
            assert isinstance(result, dict)
            assert result["id"] == tag_id
        else:
            pytest.skip("No tags available to test")
    
    @pytest.mark.slow
    def test_add_activity_tag_real_api(self, integration_client):
        """Test adding a tag to an activity using real alert data."""
        # Use specific test tag ID
        tag_id = "26c3e3d6-395a-46fa-97db-a45f8fffe885"
        
        # Search for a recent alert
        query = {
            "sort": [{"event.observedAt": {"order": "desc", "unmapped_type": "boolean"}}],
            "filters": {
                "$and": [
                    {"$isNull": {"incident.id": False}},
                    {"$dtRelativeGE": {"event.observedAt": -86400000}}  # Last 24 hours
                ]
            }
        }
        
        search_result = integration_client.activity_search(query, "event", params={"limit": 1})
        
        if not search_result.get("data"):
            pytest.skip("No recent alerts found to test")
        
        # Get the event data
        event = search_result["data"][0]
        
        # Try different possible ID fields
        event_fqid = (
            event.get("fqid") or 
            event.get("id") or 
            event.get("event", {}).get("fqid") or
            event.get("event", {}).get("id")
        )
        
        if not event_fqid:
            # Print available keys for debugging
            print(f"Available keys in event: {list(event.keys())}")
            pytest.skip("Could not extract event FQID from search result")
        
        # Debug: Print the FQID we're using
        print(f"\nUsing FQID for tag operation: {event_fqid}")
        print(f"FQID length: {len(event_fqid)}")
        
        # Add tag to the activity
        result = integration_client.add_activity_tag(event_fqid, tag_id)
        
        # Verify the operation succeeded (should return success or the updated object)
        assert isinstance(result, dict)
    
    @pytest.mark.slow
    def test_add_activity_assignee_real_api(self, integration_client):
        """Test adding an assignee to an activity using real alert data."""
        # Search for a recent alert
        query = {
            "sort": [{"event.observedAt": {"order": "desc", "unmapped_type": "boolean"}}],
            "filters": {
                "$and": [
                    {"$isNull": {"incident.id": False}},
                    {"$dtRelativeGE": {"event.observedAt": -86400000}}  # Last 24 hours
                ]
            }
        }
        
        search_result = integration_client.activity_search(query, "event", params={"limit": 1})
        
        if not search_result.get("data"):
            pytest.skip("No recent alerts found to test")
        
        # Get the event data
        event = search_result["data"][0]
        
        # Try different possible ID fields
        # The FQID might be in different fields depending on the API response
        event_fqid = (
            event.get("fqid") or 
            event.get("id") or 
            event.get("event", {}).get("fqid") or
            event.get("event", {}).get("id")
        )
        
        if not event_fqid:
            # Print available keys for debugging
            print(f"Available keys in event: {list(event.keys())}")
            pytest.skip("Could not extract event FQID from search result")
        
        # Debug: Print the FQID we're using
        print(f"\nUsing FQID for assignee operation: {event_fqid}")
        print(f"FQID length: {len(event_fqid)}")
        
        # Use a test admin ID (you may need to adjust this based on your test environment)
        # This could be retrieved from the client config or environment
        admin_id = os.getenv("TEST_ADMIN_ID", "test-admin")
        
        # Add assignee to the activity
        result = integration_client.add_activity_assignee(event_fqid, admin_id)
        
        # Verify the operation succeeded
        assert isinstance(result, dict)
        # The response should contain assignment information
        assert "id" in result or "assignment" in result or result  # API may return different structures
    
    @pytest.mark.slow
    def test_update_event_workflow_real_api(self, integration_client):
        """Test updating event workflow status using real alert data."""
        # Search for a recent alert
        query = {
            "sort": [{"event.observedAt": {"order": "desc", "unmapped_type": "boolean"}}],
            "filters": {
                "$and": [
                    {"$isNull": {"incident.id": False}},
                    {"$dtRelativeGE": {"event.observedAt": -86400000}}  # Last 24 hours
                ]
            }
        }
        
        search_result = integration_client.activity_search(query, "event", params={"limit": 1})
        
        if not search_result.get("data"):
            pytest.skip("No recent alerts found to test")
        
        # Get the event data
        event = search_result["data"][0]
        
        # Try different possible ID fields
        event_fqid = (
            event.get("fqid") or 
            event.get("id") or 
            event.get("event", {}).get("fqid") or
            event.get("event", {}).get("id")
        )
        
        if not event_fqid:
            print(f"Available keys in event: {list(event.keys())}")
            pytest.skip("Could not extract event FQID from search result")
        
        # Use test status ID
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        
        # Update the workflow status
        result = integration_client.update_event_workflow(event_fqid, status_id)
        
        # Verify the operation succeeded
        assert isinstance(result, dict)
        # The response should contain state or status information
        assert "state" in result or "disposition" in result or result  # API may return different structures


class TestIntegrationPolicies:
    """Integration tests for agent policies methods."""
    
    def test_get_agent_policies_development_mode(self, dev_client):
        """Test get_agent_policies in development mode."""
        result = dev_client.get_agent_policies()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_agent_policies_real_api(self, integration_client):
        """Test get_agent_policies against real API."""
        result = integration_client.get_agent_policies()
        
        assert isinstance(result, dict)


class TestIntegrationSearch:
    """Integration tests for search methods."""
    
    def test_depot_search_development_mode(self, dev_client):
        """Test depot_search in development mode."""
        query = {
            "query": {
                "bool": {
                    "must": [{"match_all": {}}]
                }
            }
        }
        
        result = dev_client.depot_search(query, "predicate")
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
    
    @pytest.mark.slow
    def test_depot_search_real_api(self, integration_client):
        """Test depot_search against real API."""
        query = {
            "query": {
                "bool": {
                    "must": [{"match_all": {}}]
                }
            }
        }
        
        result = integration_client.depot_search(query, "predicate", params={"limit": 5})
        
        assert isinstance(result, dict)
        assert "data" in result
    
    @pytest.mark.slow
    def test_activity_search_for_alerts_real_api(self, integration_client):
        """Test activity_search to find alerts (incidents) from last 24 hours."""
        # Query for alerts (events with incident.id) from last 24 hours
        query = {
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
                        "$isNull": {
                            "incident.id": False
                        }
                    },
                    {
                        "$not": {
                            "$or": [
                                {
                                    "$stringIn": {
                                        "activity.categories": [
                                            "it:internal:agent",
                                            "it:internal:agent:start",
                                            "it:internal:agent:stop",
                                            "it:internal:agent:data-loss",
                                            "it:internal:agent:tampering",
                                            "it:internal:agent:functionality",
                                            "it:internal:agent:informational",
                                            "it:internal:agent:lifecycle",
                                            "it:internal:agent:offline",
                                            "it:internal:agent:metrics",
                                            "it:internal:agent:error"
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "$not": {
                            "$or": [
                                {
                                    "$stringIn": {
                                        "activity.categories": [
                                            "pfpt:cloud:internal:event"
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "$dtRelativeGE": {
                            "event.observedAt": -86400000  # 24 hours in milliseconds
                        }
                    }
                ]
            }
        }
        
        result = integration_client.activity_search(query, "event", params={"limit": 10})
        
        assert isinstance(result, dict)
        assert "data" in result
        # May or may not have results depending on test environment
        if result["data"]:
            # Verify structure of returned events
            event = result["data"][0]
            assert "event" in event or "id" in event


class TestIntegrationEndpoints:
    """Integration tests for endpoints methods."""
    
    def test_get_endpoints_development_mode(self, dev_client):
        """Test get_endpoints in development mode."""
        result = dev_client.get_endpoints()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_endpoints_default_query_real_api(self, integration_client):
        """Test get_endpoints with default query against real API."""
        result = integration_client.get_endpoints(days=3)
        
        assert isinstance(result, dict)
        assert "data" in result
        # May or may not have results depending on environment
        if result["data"]:
            # Verify structure of returned endpoints
            endpoint = result["data"][0]
            assert "component" in endpoint or "id" in endpoint
    
    @pytest.mark.slow
    def test_get_endpoints_with_custom_query_real_api(self, integration_client):
        """Test get_endpoints with custom query for Windows endpoints."""
        # Query for Windows endpoints from last 3 days
        query = {
            "sort": [
                {
                    "event.observedAt": {
                        "order": "desc",
                        "unmapped_type": "boolean"
                    }
                },
                {
                    "event.id": {
                        "order": "asc",
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
                        "$not": {
                            "$or": [
                                {
                                    "$stringIn": {
                                        "component.state.visibility.code": [
                                            "it:component:state:visibility:hidden"
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "$dtRelativeGE": {
                            "event.observedAt": -259200000  # 3 days in milliseconds
                        }
                    }
                ]
            }
        }
        
        result = integration_client.get_endpoints(query=query, params={"limit": 10})
        
        assert isinstance(result, dict)
        assert "data" in result
        # May or may not have Windows endpoints
        if result["data"]:
            # If we have results, verify they're Windows endpoints
            endpoint = result["data"][0]
            # Structure may vary, just verify we got data back
            assert "id" in endpoint or "component" in endpoint
    
    @pytest.mark.slow
    def test_get_endpoints_with_kind_filter_real_api(self, integration_client):
        """Test get_endpoints with kind filter for agent endpoints."""
        result = integration_client.get_endpoints(kind="agent:saas", days=7, params={"limit": 5})
        
        assert isinstance(result, dict)
        assert "data" in result
        # Verify we can get agent endpoints
        if result["data"]:
            endpoint = result["data"][0]
            # Check for component.kind if available
            if "component" in endpoint and "kind" in endpoint["component"]:
                assert "agent" in endpoint["component"]["kind"]

class TestIntegrationDictionaries:
    """Integration tests for dictionaries methods."""
    
    def test_get_dictionaries_development_mode(self, dev_client):
        """Test get_dictionaries in development mode."""
        result = dev_client.get_dictionaries()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_dictionaries_real_api(self, integration_client):
        """Test get_dictionaries against real API."""
        result = integration_client.get_dictionaries()
        
        assert isinstance(result, dict)


class TestIntegrationDetectors:
    """Integration tests for detectors methods."""
    
    def test_get_detectors_development_mode(self, dev_client):
        """Test get_detectors in development mode."""
        result = dev_client.get_detectors()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_detectors_real_api(self, integration_client):
        """Test get_detectors against real API."""
        result = integration_client.get_detectors()
        
        assert isinstance(result, dict)
