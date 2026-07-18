from fastapi.testclient import TestClient

from app.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == "Memex Backend"
    assert "version" in data
