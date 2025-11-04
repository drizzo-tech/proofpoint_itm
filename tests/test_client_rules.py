"""
Tests for ITMClient rules methods.
"""
import pytest
import responses
from unittest.mock import Mock, patch
from proofpoint_itm.classes import Rule


class TestGetRules:
    """Test get_rules method."""
    
    @responses.activate
    def test_get_rules_success(self, mock_client, sample_rule_data):
        """Test successful retrieval of rules."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"data": [sample_rule_data]},
            status=200
        )
        
        result = mock_client.get_rules()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == sample_rule_data["id"]
    
    @responses.activate
    def test_get_rules_empty(self, mock_client):
        """Test get_rules with no results."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"data": []},
            status=200
        )
        
        result = mock_client.get_rules()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @responses.activate
    def test_get_rules_with_includes(self, mock_client, sample_rule_data):
        """Test get_rules with custom includes parameter."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"data": [sample_rule_data]},
            status=200
        )
        
        result = mock_client.get_rules(includes="id,name")
        
        assert len(responses.calls) == 1
        # URL encoding converts comma to %2C
        assert "includes=id%2Cname" in responses.calls[0].request.url or "includes=id,name" in responses.calls[0].request.url
    
    @responses.activate
    def test_get_rules_http_error(self, mock_client):
        """Test get_rules handles HTTP errors."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(Exception):
            mock_client.get_rules()
    
    def test_get_rules_development_mode(self, development_client):
        """Test get_rules in development mode returns request details."""
        result = development_client.get_rules()
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "params" in result
        assert "ruler/rules" in result["url"]


class TestGetRule:
    """Test get_rule method."""
    
    @responses.activate
    def test_get_rule_success(self, mock_client, sample_rule_data):
        """Test successful retrieval of a single rule."""
        rule_id = "rule-123"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.GET,
            url,
            json=sample_rule_data,
            status=200
        )
        
        result = mock_client.get_rule(rule_id)
        
        assert isinstance(result, dict)
        assert result["id"] == rule_id
    
    @responses.activate
    def test_get_rule_not_found(self, mock_client):
        """Test get_rule with non-existent rule ID."""
        rule_id = "nonexistent"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Not found"},
            status=404
        )
        
        with pytest.raises(Exception):
            mock_client.get_rule(rule_id)
    
    def test_get_rule_development_mode(self, development_client):
        """Test get_rule in development mode."""
        result = development_client.get_rule("rule-123")
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "ruler/rules/rule-123" in result["url"]


class TestCreateRule:
    """Test create_rule method."""
    
    @responses.activate
    def test_create_rule_success(self, mock_client):
        """Test successful rule creation."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.POST,
            url,
            json={"id": "new-rule-123"},
            status=201
        )
        
        mock_rule = Mock(spec=Rule)
        mock_rule.as_dict.return_value = {"name": "New Rule"}
        
        result = mock_client.create_rule(mock_rule)
        
        assert "id" in result
        assert result["id"] == "new-rule-123"
    
    def test_create_rule_test_mode(self, mock_client):
        """Test create_rule in test mode returns fake UUID."""
        mock_rule = Mock(spec=Rule)
        
        result = mock_client.create_rule(mock_rule, test=True)
        
        assert "id" in result
        assert isinstance(result["id"], str)
        # UUID format check
        assert len(result["id"]) == 36
    
    def test_create_rule_development_mode(self, development_client):
        """Test create_rule in development mode."""
        mock_rule = Mock(spec=Rule)
        mock_rule.as_dict.return_value = {"name": "Test Rule"}
        
        result = development_client.create_rule(mock_rule)
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
        assert result["body"]["data"][0]["name"] == "Test Rule"
    
    @responses.activate
    def test_create_rule_validation_error(self, mock_client):
        """Test create_rule with validation error."""
        url = f"{mock_client.base_url}/ruler/rules"
        
        responses.add(
            responses.POST,
            url,
            json={"error": "Validation failed"},
            status=400
        )
        
        mock_rule = Mock(spec=Rule)
        mock_rule.as_dict.return_value = {"name": ""}
        
        with pytest.raises(Exception):
            mock_client.create_rule(mock_rule)


class TestUpdateRule:
    """Test update_rule method."""
    
    @responses.activate
    def test_update_rule_success(self, mock_client):
        """Test successful rule update."""
        rule_id = "rule-123"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.PUT,
            url,
            json={"id": rule_id, "name": "Updated Rule"},
            status=200
        )
        
        mock_rule = Mock(spec=Rule)
        mock_rule.as_dict.return_value = {"name": "Updated Rule"}
        
        result = mock_client.update_rule(rule_id, mock_rule)
        
        assert result["id"] == rule_id
        assert result["name"] == "Updated Rule"
    
    def test_update_rule_test_mode(self, mock_client):
        """Test update_rule in test mode."""
        mock_rule = Mock(spec=Rule)
        
        result = mock_client.update_rule("rule-123", mock_rule, test=True)
        
        assert "id" in result
    
    @responses.activate
    def test_update_rule_not_found(self, mock_client):
        """Test update_rule with non-existent rule."""
        rule_id = "nonexistent"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.PUT,
            url,
            json={"error": "Not found"},
            status=404
        )
        
        mock_rule = Mock(spec=Rule)
        mock_rule.as_dict.return_value = {"name": "Updated"}
        
        with pytest.raises(Exception):
            mock_client.update_rule(rule_id, mock_rule)


class TestDeleteRule:
    """Test delete_rule method."""
    
    @responses.activate
    def test_delete_rule_success(self, mock_client):
        """Test successful rule deletion."""
        rule_id = "rule-123"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.DELETE,
            url,
            json={"success": True},
            status=200
        )
        
        result = mock_client.delete_rule(rule_id)
        
        assert result["success"] is True
    
    @responses.activate
    def test_delete_rule_not_found(self, mock_client):
        """Test delete_rule with non-existent rule."""
        rule_id = "nonexistent"
        url = f"{mock_client.base_url}/ruler/rules/{rule_id}"
        
        responses.add(
            responses.DELETE,
            url,
            json={"error": "Not found"},
            status=404
        )
        
        with pytest.raises(Exception):
            mock_client.delete_rule(rule_id)
    
    def test_delete_rule_development_mode(self, development_client):
        """Test delete_rule in development mode."""
        result = development_client.delete_rule("rule-123")
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "ruler/rules/rule-123" in result["url"]
