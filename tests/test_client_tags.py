"""
Tests for ITMClient tags methods.
"""
import pytest
import responses
from unittest.mock import Mock
from proofpoint_itm.classes import Tag


class TestGetTags:
    """Test get_tags method."""
    
    @responses.activate
    def test_get_tags_success(self, mock_client, sample_tag_data):
        """Test successful retrieval of tags."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.GET,
            url,
            json={"data": [sample_tag_data]},
            status=200
        )
        
        result = mock_client.get_tags()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == sample_tag_data["id"]
    
    @responses.activate
    def test_get_tags_empty(self, mock_client):
        """Test get_tags with no results."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.GET,
            url,
            json={"data": []},
            status=200
        )
        
        result = mock_client.get_tags()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @responses.activate
    def test_get_tags_with_includes(self, mock_client, sample_tag_data):
        """Test get_tags with custom includes parameter."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.GET,
            url,
            json={"data": [sample_tag_data]},
            status=200
        )
        
        result = mock_client.get_tags(includes="id,name")
        
        assert len(responses.calls) == 1
        # URL encoding converts comma to %2C
        assert "includes=id%2Cname" in responses.calls[0].request.url or "includes=id,name" in responses.calls[0].request.url
    
    @responses.activate
    def test_get_tags_http_error(self, mock_client):
        """Test get_tags handles HTTP errors."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.GET,
            url,
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(Exception):
            mock_client.get_tags()
    
    def test_get_tags_development_mode(self, development_client):
        """Test get_tags in development mode returns request details."""
        result = development_client.get_tags()
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "params" in result
        assert "depot/tags" in result["url"]


class TestGetTag:
    """Test get_tag method."""
    
    @responses.activate
    def test_get_tag_success(self, mock_client, sample_tag_data):
        """Test successful retrieval of a single tag."""
        tag_id = "tag-123"
        
        # get_tag uses depot_search internally
        url = f"{mock_client.base_url}/depot/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [sample_tag_data]},
            status=200
        )
        
        result = mock_client.get_tag(tag_id)
        
        assert isinstance(result, dict)
        assert result["id"] == sample_tag_data["id"]
    
    @responses.activate
    def test_get_tag_not_found(self, mock_client):
        """Test get_tag with non-existent tag ID."""
        tag_id = "nonexistent"
        url = f"{mock_client.base_url}/depot/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": []},
            status=200
        )
        
        # Should raise IndexError when trying to access data[0]
        with pytest.raises(IndexError):
            mock_client.get_tag(tag_id)
    
    @responses.activate
    def test_get_tag_with_params(self, mock_client, sample_tag_data):
        """Test get_tag with custom parameters."""
        tag_id = "tag-123"
        url = f"{mock_client.base_url}/depot/queries"
        
        responses.add(
            responses.POST,
            url,
            json={"data": [sample_tag_data]},
            status=200
        )
        
        result = mock_client.get_tag(tag_id, params={"limit": 1})
        
        assert isinstance(result, dict)
        assert "entityTypes=tag" in responses.calls[0].request.url


class TestCreateTag:
    """Test create_tag method."""
    
    @responses.activate
    def test_create_tag_success(self, mock_client):
        """Test successful tag creation."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.POST,
            url,
            json={"id": "new-tag-123", "name": "New Tag"},
            status=201
        )
        
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": "New Tag", "description": "Test"}
        
        result = mock_client.create_tag(mock_tag)
        
        assert "id" in result
        assert result["id"] == "new-tag-123"
    
    def test_create_tag_test_mode(self, mock_client):
        """Test create_tag in test mode returns fake UUID."""
        mock_tag = Mock(spec=Tag)
        
        result = mock_client.create_tag(mock_tag, test=True)
        
        assert "id" in result
        assert isinstance(result["id"], str)
        # UUID format check
        assert len(result["id"]) == 36
    
    def test_create_tag_development_mode(self, development_client):
        """Test create_tag in development mode."""
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": "Test Tag", "description": "Test"}
        
        result = development_client.create_tag(mock_tag)
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
        assert result["body"]["name"] == "Test Tag"
    
    @responses.activate
    def test_create_tag_validation_error(self, mock_client):
        """Test create_tag with validation error."""
        url = f"{mock_client.base_url}/depot/tags"
        
        responses.add(
            responses.POST,
            url,
            json={"error": "Validation failed"},
            status=400
        )
        
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": ""}
        
        with pytest.raises(Exception):
            mock_client.create_tag(mock_tag)


class TestUpdateTag:
    """Test update_tag method."""
    
    @responses.activate
    def test_update_tag_success(self, mock_client):
        """Test successful tag update."""
        tag_id = "tag-123"
        url = f"{mock_client.base_url}/depot/tags/{tag_id}"
        
        responses.add(
            responses.PATCH,
            url,
            json={"id": tag_id, "name": "Updated Tag"},
            status=200
        )
        
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": "Updated Tag"}
        
        result = mock_client.update_tag(tag_id, mock_tag)
        
        assert result["id"] == tag_id
        assert result["name"] == "Updated Tag"
    
    def test_update_tag_test_mode(self, mock_client):
        """Test update_tag in test mode."""
        mock_tag = Mock(spec=Tag)
        
        result = mock_client.update_tag("tag-123", mock_tag, test=True)
        
        assert "id" in result
    
    @responses.activate
    def test_update_tag_not_found(self, mock_client):
        """Test update_tag with non-existent tag."""
        tag_id = "nonexistent"
        url = f"{mock_client.base_url}/depot/tags/{tag_id}"
        
        responses.add(
            responses.PATCH,
            url,
            json={"error": "Not found"},
            status=404
        )
        
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": "Updated"}
        
        with pytest.raises(Exception):
            mock_client.update_tag(tag_id, mock_tag)
    
    def test_update_tag_development_mode(self, development_client):
        """Test update_tag in development mode."""
        mock_tag = Mock(spec=Tag)
        mock_tag.as_dict.return_value = {"name": "Updated Tag"}
        
        result = development_client.update_tag("tag-123", mock_tag)
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result


class TestAddActivityTag:
    """Test add_activity_tag method."""
    
    @responses.activate
    def test_add_activity_tag_success(self, mock_client):
        """Test successfully adding a tag to an activity."""
        fqid = "activity-123"
        tag_id = "tag-456"
        url = f"{mock_client.base_url}/activity/events/{fqid}/tags"
        
        responses.add(
            responses.PATCH,
            url,
            json={"success": True},
            status=200
        )
        
        result = mock_client.add_activity_tag(fqid, tag_id)
        
        assert result["success"] is True
        assert "tagValue=tag-456" in responses.calls[0].request.url
    
    @responses.activate
    def test_add_activity_tag_with_custom_params(self, mock_client):
        """Test add_activity_tag with custom parameters."""
        fqid = "activity-123"
        tag_id = "tag-456"
        url = f"{mock_client.base_url}/activity/events/{fqid}/tags"
        
        responses.add(
            responses.PATCH,
            url,
            json={"success": True},
            status=200
        )
        
        params = {"additional": "param"}
        result = mock_client.add_activity_tag(fqid, tag_id, params=params)
        
        request_url = responses.calls[0].request.url
        assert "tagValue=tag-456" in request_url
        assert "additional=param" in request_url
    
    @responses.activate
    def test_add_activity_tag_not_found(self, mock_client):
        """Test add_activity_tag with non-existent activity."""
        fqid = "nonexistent"
        tag_id = "tag-456"
        url = f"{mock_client.base_url}/activity/events/{fqid}/tags"
        
        responses.add(
            responses.PATCH,
            url,
            json={"error": "Activity not found"},
            status=404
        )
        
        with pytest.raises(Exception):
            mock_client.add_activity_tag(fqid, tag_id)
    
    def test_add_activity_tag_development_mode(self, development_client):
        """Test add_activity_tag in development mode."""
        result = development_client.add_activity_tag("activity-123", "tag-456")
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "params" in result
        assert result["params"]["tagValue"] == "tag-456"
