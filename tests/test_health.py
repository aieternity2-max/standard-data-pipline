from fastapi.testclient import TestClient

from app.api.app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "Standard Data Pipeline"
    assert data["status"] in ["healthy", "unhealthy"]
    assert data["database"] in ["healthy", "unhealthy"]
    assert data["vector_store"] in ["healthy", "unhealthy"]