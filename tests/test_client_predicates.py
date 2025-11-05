"""
Tests for ITMClient predicates methods.
"""
import pytest
import responses
from unittest.mock import Mock
from proofpoint_itm.classes import Predicate


class TestGetPredicates:
    """Test get_predicates method."""
    
    @responses.activate
    def test_get_predicates_success(self, mock_client, sample_predicate_data):
        """Test successful retrieval of predicates."""
        url = f"{mock_client.base_url}/depot/predicates"
        
        responses.add(
            responses.GET,
            url,
            json={"data": [sample_predicate_data]},
            status=200
        )
        
        result = mock_client.get_predicates()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == sample_predicate_data["id"]
    
    @responses.activate
    def test_get_predicates_empty(self, mock_client):
        """Test get_predicates with no results."""
        url = f"{mock_client.base_url}/depot/predicates"
        
        responses.add(
            responses.GET,
            url,
            json={"data": []},
            status=200
        )
        
        result = mock_client.get_predicates()
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestGetPredicate:
    """Test get_predicate method."""
    
    @responses.activate
    def test_get_predicate_success(self, mock_client, sample_predicate_data):
        """Test successful retrieval of a single predicate."""
        predicate_id = "predicate-123"
        url = f"{mock_client.base_url}/depot/predicates/{predicate_id}"
        
        responses.add(
            responses.GET,
            url,
            json=sample_predicate_data,
            status=200
        )
        
        result = mock_client.get_predicate(predicate_id)
        
        assert isinstance(result, dict)
        assert result["id"] == predicate_id


class TestGetConditions:
    """Test get_conditions method (filtered predicates)."""
    
    @responses.activate
    def test_get_conditions_filters_correctly(self, mock_client):
        """Test get_conditions filters for custom match predicates."""
        url = f"{mock_client.base_url}/depot/predicates"
        
        predicates = [
            {"id": "pred-1", "kind": "it:predicate:custom:match", "name": "Condition 1"},
            {"id": "pred-2", "kind": "it:predicate:builtin", "name": "Builtin"},
            {"id": "pred-3", "kind": "it:predicate:custom:match", "name": "Condition 2"},
        ]
        
        responses.add(
            responses.GET,
            url,
            json={"data": predicates},
            status=200
        )
        
        result = mock_client.get_conditions()
        
        # Should only return custom:match predicates
        assert len(result) == 2
        assert all(p["kind"] == "it:predicate:custom:match" for p in result)


class TestCreatePredicate:
    """Test create_predicate method."""
    
    @responses.activate
    def test_create_predicate_success(self, mock_client):
        """Test successful predicate creation."""
        url = f"{mock_client.base_url}/depot/predicates"
        
        responses.add(
            responses.POST,
            url,
            json={"id": "new-predicate-123"},
            status=201
        )
        
        mock_predicate = Mock(spec=Predicate)
        mock_predicate.as_dict.return_value = {"name": "New Predicate"}
        
        result = mock_client.create_predicate(mock_predicate)
        
        assert "id" in result
        assert result["id"] == "new-predicate-123"
    
    def test_create_predicate_test_mode(self, mock_client):
        """Test create_predicate in test mode."""
        mock_predicate = Mock(spec=Predicate)
        
        result = mock_client.create_predicate(mock_predicate, test=True)
        
        assert "id" in result
        assert isinstance(result["id"], str)


class TestUpdatePredicate:
    """Test update_predicate method (PATCH)."""
    
    @responses.activate
    def test_update_predicate_success(self, mock_client):
        """Test successful predicate update with PATCH."""
        predicate_id = "predicate-123"
        url = f"{mock_client.base_url}/depot/predicates/{predicate_id}"
        
        responses.add(
            responses.PATCH,
            url,
            json={"id": predicate_id, "name": "Updated Predicate"},
            status=200
        )
        
        mock_predicate = Mock(spec=Predicate)
        mock_predicate.as_dict.return_value = {"name": "Updated Predicate"}
        
        result = mock_client.update_predicate(predicate_id, mock_predicate)
        
        assert result["id"] == predicate_id
        assert result["name"] == "Updated Predicate"


class TestOverwritePredicate:
    """Test overwrite_predicate method (PUT)."""
    
    @responses.activate
    def test_overwrite_predicate_success(self, mock_client):
        """Test successful predicate overwrite with PUT."""
        predicate_id = "predicate-123"
        url = f"{mock_client.base_url}/depot/predicates/{predicate_id}"
        
        responses.add(
            responses.PUT,
            url,
            json={"id": predicate_id, "name": "Overwritten Predicate"},
            status=200
        )
        
        mock_predicate = Mock(spec=Predicate)
        mock_predicate.as_dict.return_value = {"name": "Overwritten Predicate"}
        
        result = mock_client.overwrite_predicate(predicate_id, mock_predicate)
        
        assert result["id"] == predicate_id
        assert result["name"] == "Overwritten Predicate"


class TestDeletePredicate:
    """Test delete_predicate method."""
    
    @responses.activate
    def test_delete_predicate_success(self, mock_client):
        """Test successful predicate deletion."""
        predicate_id = "predicate-123"
        url = f"{mock_client.base_url}/depot/predicates/{predicate_id}"
        
        responses.add(
            responses.DELETE,
            url,
            json={"success": True},
            status=200
        )
        
        result = mock_client.delete_predicate(predicate_id)
        
        assert result["success"] is True
