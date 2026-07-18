from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_endpoint_returns_results():
    response = client.post("/search/", json={"query": "example"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["results"], list)
