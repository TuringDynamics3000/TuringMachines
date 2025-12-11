"""
Test suite for /v1/biometrics/upload endpoint
"""
import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

# Import the FastAPI app
import sys
sys.path.insert(0, '..')
from main import app

client = TestClient(app)


def create_test_image() -> bytes:
    """Create a minimal test JPEG image"""
    img = Image.new('RGB', (112, 112), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()


def test_upload_endpoint_success():
    """Test successful selfie upload"""
    img_bytes = create_test_image()
    files = {"selfie": ("test.jpg", img_bytes, "image/jpeg")}

    response = client.post("/v1/biometrics/upload?tenant_id=test", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "liveness" in data
    assert "embedding_status" in data


def test_upload_endpoint_liveness_structure():
    """Test that liveness data has expected structure"""
    img_bytes = create_test_image()
    files = {"selfie": ("test.jpg", img_bytes, "image/jpeg")}

    response = client.post("/v1/biometrics/upload?tenant_id=test", files=files)
    assert response.status_code == 200
    data = response.json()
    
    liveness = data["liveness"]
    assert "score" in liveness
    assert "is_live" in liveness
    assert "blink_rate" in liveness
    assert "mouth_ratio" in liveness
    assert "head_pose_magnitude" in liveness
    assert "reason" in liveness


def test_upload_endpoint_session_id_format():
    """Test that session_id has expected format"""
    img_bytes = create_test_image()
    files = {"selfie": ("test.jpg", img_bytes, "image/jpeg")}

    response = client.post("/v1/biometrics/upload?tenant_id=test", files=files)
    assert response.status_code == 200
    data = response.json()
    
    session_id = data["session_id"]
    assert session_id.startswith("sess_")
    assert len(session_id) > 5


def test_upload_endpoint_invalid_image():
    """Test upload with invalid image data"""
    invalid_bytes = b"not an image"
    files = {"selfie": ("test.jpg", invalid_bytes, "image/jpeg")}

    response = client.post("/v1/biometrics/upload?tenant_id=test", files=files)
    # Should return 400 or 422 for invalid image
    assert response.status_code in [400, 422]


def test_upload_endpoint_missing_file():
    """Test upload without file"""
    response = client.post("/v1/biometrics/upload?tenant_id=test")
    # Should return 422 for missing required field
    assert response.status_code == 422


def test_upload_endpoint_tenant_id():
    """Test upload with different tenant IDs"""
    img_bytes = create_test_image()
    files = {"selfie": ("test.jpg", img_bytes, "image/jpeg")}

    # Test with custom tenant
    response = client.post("/v1/biometrics/upload?tenant_id=geniusto", files=files)
    assert response.status_code == 200
    
    # Test with default tenant
    response = client.post("/v1/biometrics/upload", files=files)
    assert response.status_code == 200


def test_upload_endpoint_embedding_status():
    """Test that embedding status is returned"""
    img_bytes = create_test_image()
    files = {"selfie": ("test.jpg", img_bytes, "image/jpeg")}

    response = client.post("/v1/biometrics/upload?tenant_id=test", files=files)
    assert response.status_code == 200
    data = response.json()
    
    # Embedding status should be either "ok" or "face_not_detected"
    assert data["embedding_status"] in ["ok", "face_not_detected"]
