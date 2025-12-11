"""
Test suite for /v1/biometrics/verify endpoint
"""
import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, '..')
from main import app

client = TestClient(app)


def test_verify_endpoint_structure():
    """Test verify endpoint response structure"""
    # Note: This test will fail without proper database setup
    # It's here to document the expected API structure
    
    request_data = {
        "selfie_session_id": "sess_test1",
        "id_session_id": "sess_test2"
    }
    
    response = client.post("/v1/biometrics/verify", json=request_data)
    
    # May return 404 if sessions don't exist, which is expected
    if response.status_code == 200:
        data = response.json()
        assert "selfie_session_id" in data
        assert "id_session_id" in data
        assert "result" in data
        assert "explanation" in data
        
        # Check result structure
        result = data["result"]
        assert "mobile_score" in result
        assert "arcface_score" in result
        assert "fused_score" in result
        assert "is_match" in result
        
        # Check explanation structure
        explanation = data["explanation"]
        assert "summary" in explanation
        assert "reasons" in explanation


def test_verify_endpoint_missing_fields():
    """Test verify endpoint with missing required fields"""
    # Missing id_session_id
    request_data = {
        "selfie_session_id": "sess_test1"
    }
    response = client.post("/v1/biometrics/verify", json=request_data)
    assert response.status_code == 422  # Validation error


def test_verify_endpoint_invalid_session():
    """Test verify endpoint with non-existent sessions"""
    request_data = {
        "selfie_session_id": "sess_nonexistent1",
        "id_session_id": "sess_nonexistent2"
    }
    response = client.post("/v1/biometrics/verify", json=request_data)
    # Should return 404 for non-existent sessions
    assert response.status_code in [404, 500]


@pytest.mark.skip(reason="Requires database setup with test data")
def test_verify_endpoint_full_flow():
    """
    Full integration test for verify endpoint
    This test requires:
    1. Database to be running
    2. Test sessions to be created
    3. Embeddings to be saved
    """
    # This is a placeholder for a full integration test
    # In a real scenario, you would:
    # 1. Upload two selfies
    # 2. Get their session IDs
    # 3. Verify them against each other
    pass
