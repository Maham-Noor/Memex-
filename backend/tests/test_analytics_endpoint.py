from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analytics_endpoint_returns_summary():
    response = client.post("/analytics/", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "summary" in response.json()
