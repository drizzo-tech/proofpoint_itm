"""
Tests for ITMClient workflow methods.
"""
import pytest
import responses


class TestUpdateEventWorkflow:
    """Test update_event_workflow method."""
    
    @responses.activate
    def test_update_event_workflow_success(self, mock_client):
        """Test successful workflow status update."""
        fqid = "b2l0cm9vdC1vcDEtYWN0aXZpdHktZXZlbnRzIzEyMzQ1Njc4OTA="
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"success": True, "state": {"disposition": {"status": {"id": status_id}}}},
            status=200
        )
        
        result = mock_client.update_event_workflow(fqid, status_id)
        
        assert isinstance(result, dict)
        assert "success" in result or "state" in result
        
        # Verify the request body structure
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        import json
        body = json.loads(request_body)
        assert body == {"state": {"disposition": {"status": {"id": status_id}}}}
    
    @responses.activate
    def test_update_event_workflow_body_structure(self, mock_client):
        """Test that the request body has correct nested structure."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"updated": True},
            status=200
        )
        
        result = mock_client.update_event_workflow(fqid, status_id)
        
        # Verify the exact body structure
        import json
        request_body = json.loads(responses.calls[0].request.body)
        
        assert "state" in request_body
        assert "disposition" in request_body["state"]
        assert "status" in request_body["state"]["disposition"]
        assert "id" in request_body["state"]["disposition"]["status"]
        assert request_body["state"]["disposition"]["status"]["id"] == status_id
    
    @responses.activate
    def test_update_event_workflow_different_status_ids(self, mock_client):
        """Test workflow update with different status IDs."""
        fqid = "test-fqid"
        status_ids = [
            "3e37bcdb-7816-4b70-bead-f329de788951",  # Example status
            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # Another status
            "00000000-0000-0000-0000-000000000000",  # Null UUID
        ]
        
        for status_id in status_ids:
            url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
            
            responses.add(
                responses.PATCH,
                url,
                json={"status_id": status_id},
                status=200
            )
            
            result = mock_client.update_event_workflow(fqid, status_id)
            assert isinstance(result, dict)
    
    @responses.activate
    def test_update_event_workflow_with_custom_headers(self, mock_client):
        """Test workflow update with custom headers."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        custom_headers = {"X-Custom-Header": "test-value"}
        
        responses.add(
            responses.PATCH,
            url,
            json={"success": True},
            status=200
        )
        
        result = mock_client.update_event_workflow(fqid, status_id, headers=custom_headers)
        
        assert isinstance(result, dict)
        # Verify custom headers were sent
        assert "X-Custom-Header" in responses.calls[0].request.headers
    
    @responses.activate
    def test_update_event_workflow_not_found(self, mock_client):
        """Test workflow update with non-existent event."""
        fqid = "nonexistent-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"error": "Event not found"},
            status=404
        )
        
        with pytest.raises(Exception):
            mock_client.update_event_workflow(fqid, status_id)
    
    @responses.activate
    def test_update_event_workflow_invalid_status(self, mock_client):
        """Test workflow update with invalid status ID."""
        fqid = "test-fqid"
        status_id = "invalid-status-id"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"error": "Invalid status ID"},
            status=400
        )
        
        with pytest.raises(Exception):
            mock_client.update_event_workflow(fqid, status_id)
    
    @responses.activate
    def test_update_event_workflow_server_error(self, mock_client):
        """Test workflow update handles server errors."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"error": "Internal server error"},
            status=500
        )
        
        with pytest.raises(Exception):
            mock_client.update_event_workflow(fqid, status_id)
    
    def test_update_event_workflow_development_mode(self, development_client):
        """Test update_event_workflow in development mode."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        
        result = development_client.update_event_workflow(fqid, status_id)
        
        assert isinstance(result, dict)
        assert "url" in result
        assert "body" in result
        assert "headers" in result
        
        # Verify the body structure in dev mode
        assert result["body"] == {
            "state": {
                "disposition": {
                    "status": {
                        "id": status_id
                    }
                }
            }
        }
        assert f"activity/events/{fqid}/annotations/workflow" in result["url"]
    
    def test_update_event_workflow_development_mode_with_headers(self, development_client):
        """Test update_event_workflow in development mode with custom headers."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        custom_headers = {"X-Test": "value"}
        
        result = development_client.update_event_workflow(fqid, status_id, headers=custom_headers)
        
        assert result["headers"] == custom_headers
        assert result["body"]["state"]["disposition"]["status"]["id"] == status_id
    
    @responses.activate
    def test_update_event_workflow_fqid_with_padding(self, mock_client):
        """Test workflow update with base64 FQID containing padding."""
        # FQID with base64 padding
        fqid = "b2l0cm9vdC1vcDEtYWN0aXZpdHktZXZlbnRzIzEyMzQ1Njc4OTA=="
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        responses.add(
            responses.PATCH,
            url,
            json={"success": True},
            status=200
        )
        
        result = mock_client.update_event_workflow(fqid, status_id)
        
        assert isinstance(result, dict)
        # Verify the FQID was used correctly in the URL
        assert fqid in responses.calls[0].request.url
    
    @responses.activate
    def test_update_event_workflow_response_structure(self, mock_client):
        """Test that response is properly parsed."""
        fqid = "test-fqid"
        status_id = "3e37bcdb-7816-4b70-bead-f329de788951"
        url = f"{mock_client.base_url}/activity/events/{fqid}/annotations/workflow"
        
        expected_response = {
            "id": "event-123",
            "state": {
                "disposition": {
                    "status": {
                        "id": status_id,
                        "name": "Resolved"
                    }
                }
            },
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        responses.add(
            responses.PATCH,
            url,
            json=expected_response,
            status=200
        )
        
        result = mock_client.update_event_workflow(fqid, status_id)
        
        assert result == expected_response
        assert result["state"]["disposition"]["status"]["id"] == status_id
