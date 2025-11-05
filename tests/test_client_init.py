"""
Tests for ITMClient initialization and authentication.
"""
import pytest
import responses
from unittest.mock import patch, Mock
from proofpoint_itm.client import ITMClient


class TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_client_init_with_valid_config(self, mock_config, mock_token_response):
        """Test client initializes successfully with valid config."""
        with patch.object(ITMClient, 'get_token', return_value=mock_token_response):
            client = ITMClient(mock_config)
            
            assert client.client_id == mock_config["client_id"]
            assert client.tenant_id == mock_config["tenant_id"]
            assert client.client_secret == mock_config["client_secret"]
            assert client.base_url == f"https://{mock_config['tenant_id']}.explore.proofpoint.com/v2/apis"
            assert client.development_mode is False
            assert client.timeout == 30
    
    def test_client_init_with_custom_timeout(self, mock_config, mock_token_response):
        """Test client initialization with custom timeout."""
        with patch.object(ITMClient, 'get_token', return_value=mock_token_response):
            client = ITMClient(mock_config, timeout=60)
            assert client.timeout == 60
    
    def test_client_init_development_mode(self, mock_config, mock_token_response):
        """Test client initialization in development mode."""
        with patch.object(ITMClient, 'get_token', return_value=mock_token_response):
            client = ITMClient(mock_config, development=True)
            assert client.development_mode is True
    
    def test_client_init_missing_config_key(self):
        """Test client initialization fails with missing config keys."""
        incomplete_config = {"client_id": "test"}
        
        with pytest.raises(KeyError):
            with patch.object(ITMClient, 'get_token', return_value={"access_token": "test"}):
                ITMClient(incomplete_config)


class TestAuthentication:
    """Test authentication and token management."""
    
    @responses.activate
    def test_get_token_success(self, mock_config):
        """Test successful token retrieval."""
        token_url = f"https://{mock_config['tenant_id']}.explore.proofpoint.com/v2/apis/auth/oauth/token"
        
        responses.add(
            responses.POST,
            token_url,
            json={
                "access_token": "test-token-123",
                "token_type": "Bearer",
                "expires_in": 3600
            },
            status=200
        )
        
        # Don't mock get_token for this test
        client = ITMClient(mock_config)
        
        assert client.session.headers["Authorization"] == "Bearer test-token-123"
    
    @responses.activate
    def test_get_token_failure_invalid_credentials(self, mock_config):
        """Test token retrieval fails with invalid credentials."""
        token_url = f"https://{mock_config['tenant_id']}.explore.proofpoint.com/v2/apis/auth/oauth/token"
        
        responses.add(
            responses.POST,
            token_url,
            json={"error": "invalid_client"},
            status=401
        )
        
        with pytest.raises(Exception, match="Failed to get token"):
            ITMClient(mock_config)
    
    @responses.activate
    def test_get_token_network_error(self, mock_config):
        """Test token retrieval handles network errors."""
        token_url = f"https://{mock_config['tenant_id']}.explore.proofpoint.com/v2/apis/auth/oauth/token"
        
        responses.add(
            responses.POST,
            token_url,
            body=Exception("Network error")
        )
        
        with pytest.raises(Exception):
            ITMClient(mock_config)
    
    def test_session_headers_set_correctly(self, mock_client):
        """Test that session headers are set with Bearer token."""
        assert "Authorization" in mock_client.session.headers
        assert mock_client.session.headers["Authorization"].startswith("Bearer ")


class TestURLBuilding:
    """Test URL construction methods."""
    
    def test_build_url(self, mock_client):
        """Test URL building with endpoint."""
        endpoint = "ruler/rules"
        expected_url = f"{mock_client.base_url}/{endpoint}"
        
        result = mock_client.build_url(endpoint)
        
        assert result == expected_url
    
    def test_build_url_with_id(self, mock_client):
        """Test URL building with resource ID."""
        endpoint = "ruler/rules/rule-123"
        expected_url = f"{mock_client.base_url}/{endpoint}"
        
        result = mock_client.build_url(endpoint)
        
        assert result == expected_url


class TestParameterPreparation:
    """Test parameter preparation helper methods."""
    
    def test_prepare_params_with_none(self, mock_client):
        """Test parameter preparation with None params."""
        defaults = {"includes": "*", "limit": 100}
        
        result = mock_client._prepare_params(defaults, None)
        
        assert result == defaults
    
    def test_prepare_params_with_custom(self, mock_client):
        """Test parameter preparation with custom params."""
        defaults = {"includes": "*", "limit": 100}
        custom = {"limit": 50, "offset": 10}
        
        result = mock_client._prepare_params(defaults, custom)
        
        assert result["includes"] == "*"  # Default preserved
        assert result["limit"] == 50  # Custom overrides default
        assert result["offset"] == 10  # Custom added
    
    def test_prepare_params_empty_custom(self, mock_client):
        """Test parameter preparation with empty custom params."""
        defaults = {"includes": "*"}
        custom = {}
        
        result = mock_client._prepare_params(defaults, custom)
        
        assert result["includes"] == "*"
