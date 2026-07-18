from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_settings_endpoint_returns_settings():
    response = client.get("/settings/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "settings" in response.json()
