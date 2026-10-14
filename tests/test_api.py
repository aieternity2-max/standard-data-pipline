from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

from app.api.app import app
from app.models.document import Document

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app_name" in data
    assert "mysql" in data
    assert "chromadb" in data


def test_api_overview():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "document_count" in data
    assert "mysql_connected" in data
    assert "supported_formats" in data
    assert "workflow_steps" in data


def test_api_get_documents():
    response = client.get("/api/documents?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


def test_api_search():
    response = client.post("/api/search", json={"query": "test search query", "n_results": 3})
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_api_search_empty_query_error():
    response = client.post("/api/search", json={"query": "   ", "n_results": 3})
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]


def test_api_rag_ask_mock(monkeypatch):
    mock_rag_service = MagicMock()
    mock_rag_service.answer.return_value = {
        "answer": "Test answer from AI.",
        "context": "Context snippet.",
        "sources": ["sample.csv"],
        "result_count": 1,
    }
    monkeypatch.setattr("app.api.app.RAGService", lambda: mock_rag_service)

    response = client.post("/api/rag/ask", json={"query": "What is Python?", "n_results": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test answer from AI."
    assert data["result_count"] == 1


def test_api_rag_ask_empty_query_error():
    response = client.post("/api/rag/ask", json={"query": "", "n_results": 2})
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]


def test_api_dashboards():
    response = client.get("/api/dashboards")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_api_upload_preview_no_files():
    response = client.post("/api/upload/preview", files={})
    assert response.status_code == 422 or response.status_code == 400


def test_api_upload_preview_with_csv():
    csv_content = b"customer_id,name,city\n1,Alice,Bengaluru\n2,Bob,Mumbai\n"
    files = [("files", ("test_sample.csv", csv_content, "text/csv"))]
    response = client.post("/api/upload/preview", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 2
    assert len(data["file_results"]) == 1
    assert data["file_results"][0]["file"] == "test_sample.csv"
