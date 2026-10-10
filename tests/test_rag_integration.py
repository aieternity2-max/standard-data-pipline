from uuid import uuid4

import pytest

from app.llm.mock_provider import MockLLMProvider
from app.models.document import Document
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.rag.context_builder import RAGContextBuilder
from app.rag.rag_service import RAGService
from app.search.search_service import SearchService
from app.storage.vector_storage import VectorStorage


class FakeSQLStorage:
    """Prevent integration tests from requiring a live MySQL database."""

    def __init__(self):
        self.documents = []

    def save(self, documents):
        self.documents.extend(documents)
        return len(documents)


@pytest.fixture
def isolated_rag_environment(tmp_path, monkeypatch):
    """Create isolated ChromaDB storage for this test."""

    from app.config.settings import settings

    collection_name = f"rag_integration_{uuid4().hex}"

    monkeypatch.setattr(
        settings,
        "chroma_path",
        str(tmp_path / "chroma"),
    )

    monkeypatch.setattr(
        settings,
        "chroma_collection",
        collection_name,
    )

    monkeypatch.setattr(
        "app.pipeline.ingestion_pipeline.SQLStorage",
        FakeSQLStorage,
    )

    return collection_name


def test_end_to_end_ingestion_search_and_rag(
    isolated_rag_environment,
):
    """Test ingestion, embedding, retrieval, and RAG together."""

    collection_name = isolated_rag_environment

    documents = [
        Document(
            id="rag-integration-001",
            source="integration_test.txt",
            source_type="txt",
            content=(
                "The Orion platform retains database backups "
                "for 45 days. Database backups are encrypted "
                "and verified every morning."
            ),
            metadata={"category": "backup_policy"},
        ),
        Document(
            id="rag-integration-002",
            source="integration_test.txt",
            source_type="txt",
            content=(
                "The customer support team operates from "
                "Bengaluru and handles account enquiries."
            ),
            metadata={"category": "customer_support"},
        ),
    ]

    # 1. Ingest documents through the existing production pipeline.
    pipeline = IngestionPipeline()
    processed_documents = pipeline.run(documents)

    assert processed_documents, (
        "The ingestion pipeline returned no processed documents."
    )

    assert pipeline.last_embeddings, (
        "The pipeline did not record generated embeddings."
    )

    assert len(pipeline.last_embeddings) == len(processed_documents)

    # 2. Verify that the documents were stored in real ChromaDB.
    vector_storage = VectorStorage(
        collection_name=collection_name,
    )

    assert vector_storage.count() > 0, (
        "No documents were stored in the ChromaDB collection."
    )

    # 3. Exercise the SearchService directly.
    search_service = SearchService(
        vector_storage=vector_storage,
    )

    search_results = search_service.search(
        query="How long are database backups retained?",
        n_results=5,
    )

    assert search_results["documents"], (
        "Semantic search returned no document results."
    )

    retrieved_documents = search_results["documents"][0]

    assert any(
        "45 days" in content
        for content in retrieved_documents
    ), (
        "Semantic search did not retrieve the backup-retention policy."
    )

    # 4. Build the RAG context using the same real search service.
    context_builder = RAGContextBuilder(
        search_service=search_service,
    )

    rag_context = context_builder.build(
        query="How long are database backups retained?",
        n_results=5,
    )

    assert rag_context["result_count"] > 0
    assert "45 days" in rag_context["context"]
    assert rag_context["sources"]

    # 5. Generate the RAG response using the actual mock provider.
    rag_service = RAGService(
        context_builder=context_builder,
        llm_provider=MockLLMProvider(),
    )

    response = rag_service.answer(
        query="How long are database backups retained?",
        n_results=5,
    )

    # 6. Verify the standardized RAG response.
    assert response["query"] == (
        "How long are database backups retained?"
    )

    assert response["answer"] == (
        "Mock LLM response generated "
        "from the supplied context."
    )

    assert "45 days" in response["context"]
    assert response["result_count"] > 0
    assert response["sources"]

    assert any(
        "45 days" in source["content"]
        for source in response["sources"]
    ), (
        "The RAG response sources do not contain the expected policy."
    )