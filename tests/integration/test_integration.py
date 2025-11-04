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
        """Test adding a tag to an activity (if we have both)."""
        # This test would require a valid activity FQID and tag ID
        # Skip for now unless we have test data
        pytest.skip("Requires valid activity FQID and tag ID for testing")


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


class TestIntegrationEndpoints:
    """Integration tests for endpoints methods."""
    
    def test_get_endpoints_development_mode(self, dev_client):
        """Test get_endpoints in development mode."""
        result = dev_client.get_endpoints()
        
        assert isinstance(result, dict)
        assert "url" in result
    
    @pytest.mark.slow
    def test_get_endpoints_real_api(self, integration_client):
        """Test get_endpoints against real API."""
        result = integration_client.get_endpoints(days=1)
        
        assert isinstance(result, dict)


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
