"""FastAPI app startup tests."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    """Health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_homepage():
    """Homepage returns 200 with HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text or "<html" in response.text


def test_batch_page():
    """Batch scan page returns 200."""
    response = client.get("/batch")
    assert response.status_code == 200


def test_dashboard_page():
    """Scan results page returns 200 for scan_id=1."""
    response = client.get("/scan/1")
    assert response.status_code == 200


def test_static_css():
    """Static CSS file is served."""
    response = client.get("/static/css/style.css")
    assert response.status_code == 200


def test_static_charts_js():
    """Static charts JS file is served."""
    response = client.get("/static/js/charts.js")
    assert response.status_code == 200
