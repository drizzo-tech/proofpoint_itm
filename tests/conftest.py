"""
Shared pytest fixtures for Proofpoint ITM API client tests.
"""
import pytest
import responses
from unittest.mock import Mock, patch
from proofpoint_itm.client import ITMClient


@pytest.fixture
def mock_config():
    """Provide a mock configuration dictionary."""
    return {
        "client_id": "test-client-id",
        "tenant_id": "test-tenant",
        "client_secret": "test-secret"
    }


@pytest.fixture
def mock_token_response():
    """Provide a mock token response."""
    return {
        "access_token": "mock-access-token",
        "token_type": "Bearer",
        "expires_in": 3600
    }


@pytest.fixture
def mock_client(mock_config, mock_token_response):
    """
    Create a mock ITM client with patched authentication.
    
    This fixture mocks the token retrieval so we don't hit the real API
    during initialization.
    """
    with patch.object(ITMClient, 'get_token', return_value=mock_token_response):
        client = ITMClient(mock_config)
        return client


@pytest.fixture
def development_client(mock_config):
    """
    Create a client in development mode.
    
    Development mode returns request details instead of making actual API calls.
    """
    with patch.object(ITMClient, 'get_token', return_value={"access_token": "test", "token_type": "Bearer"}):
        client = ITMClient(mock_config, development=True)
        return client


@pytest.fixture
def mock_responses():
    """
    Activate responses library for mocking HTTP requests.
    
    Usage in tests:
        def test_something(mock_responses):
            mock_responses.add(
                responses.GET,
                "https://test-tenant.explore.proofpoint.com/v2/apis/ruler/rules",
                json={"data": []},
                status=200
            )
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_rule_data():
    """Provide sample rule data for testing."""
    return {
        "id": "rule-123",
        "name": "Test Rule",
        "description": "A test rule",
        "enabled": True,
        "severity": "high"
    }


@pytest.fixture
def sample_predicate_data():
    """Provide sample predicate data for testing."""
    return {
        "id": "predicate-123",
        "name": "Test Predicate",
        "kind": "it:predicate:custom:match",
        "description": "A test predicate"
    }


@pytest.fixture
def sample_tag_data():
    """Provide sample tag data for testing."""
    return {
        "id": "tag-123",
        "name": "Test Tag",
        "description": "A test tag"
    }


@pytest.fixture
def sample_policy_data():
    """Provide sample agent policy data for testing."""
    return {
        "id": "policy-123",
        "name": "Test Policy",
        "description": "A test policy"
    }


@pytest.fixture
def sample_dictionary_data():
    """Provide sample dictionary data for testing."""
    return {
        "id": "dict-123",
        "name": "Test Dictionary",
        "description": "A test dictionary"
    }


@pytest.fixture
def sample_detector_data():
    """Provide sample detector data for testing."""
    return {
        "id": "detector-123",
        "name": "Test Detector",
        "description": "A test detector"
    }


@pytest.fixture
def sample_search_query():
    """Provide a sample Elasticsearch query for testing."""
    return {
        "query": {
            "bool": {
                "must": [
                    {"match": {"field": "value"}}
                ]
            }
        }
    }
