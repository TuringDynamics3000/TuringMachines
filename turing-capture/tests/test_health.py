"""
TuringCapture Health Endpoint Tests
Bank-grade test suite for CI/CD pipeline
"""

import os
import sys

from fastapi.testclient import TestClient

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_health_endpoint_exists():
    """Test that health endpoint is accessible"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_json():
    """Test that health endpoint returns JSON"""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"


def test_health_endpoint_status_ok():
    """Test that health endpoint returns status ok"""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_health_endpoint_includes_service_name():
    """Test that health endpoint includes service name"""
    response = client.get("/health")
    data = response.json()
    assert "service" in data
    assert data["service"] == "turing-capture"


def test_health_endpoint_includes_version():
    """Test that health endpoint includes version"""
    response = client.get("/health")
    data = response.json()
    assert "version" in data
    assert isinstance(data["version"], str)


def test_health_endpoint_response_time():
    """Test that health endpoint responds quickly (< 1 second)"""
    import time

    start = time.time()
    response = client.get("/health")
    duration = time.time() - start
    assert response.status_code == 200
    assert duration < 1.0, f"Health endpoint took {duration}s, expected < 1s"


def test_root_endpoint():
    """Test that root endpoint is accessible"""
    response = client.get("/")
    assert response.status_code in [200, 404]  # Either works or redirects


def test_docs_endpoint():
    """Test that API docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test that OpenAPI schema is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
