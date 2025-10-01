import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api import app

@pytest.fixture(scope="module")
def client():
    """FastAPI test client"""
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    """Test: Health check returns 200"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "printers" in data
    assert "active_jobs" in data

def test_create_job(client):
    """Test: creation of a job endpoint via POST"""
    job_data = {
        "id": "test_001",
        "material": "PLA",
        "est_time": 10.0,
        "priority": 1
    }

    response = client.post("/jobs", json=job_data)
    assert response.status_code == 201

    data = response.json()

    assert data["id"] == "test_001"
    assert data["material"] == "PLA"
    assert data["status"] == "queue"

def test_list_jobs(client):
    """Test: list endpoint via GET"""

    response = client.get("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)

def test_get_stats(client):
    """Test: stats endpoint via GET"""

    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert "avg_wait_time" in data

def test_cancel_nonexistent_job(client):
    """Test: Cancel non-existent job returns 404"""
    
    response = client.delete("/jobs/nonexistent_job")
    assert response.status_code == 404

