import pytest

from app.llm.mock_provider import MockLLMProvider
from app.models.document import Document
from app.rag.context_builder import RAGContextBuilder
from app.rag.rag_service import RAGService
from app.search.search_service import SearchService
from app.storage.vector_storage import VectorStorage


def create_rag_service(
    collection_name="test_rag_service",
    llm_provider=None,
):
    """
    Create a RAG service with test documents and vector storage.
    """

    storage = VectorStorage(
        collection_name=collection_name
    )

    documents = [
        Document(
            id=f"{collection_name}-1",
            source="python.txt",
            source_type="txt",
            content=(
                "Python is a programming language "
                "used for data analysis and automation."
            ),
            metadata={"topic": "Python"},
        ),
        Document(
            id=f"{collection_name}-2",
            source="mysql.txt",
            source_type="txt",
            content=(
                "MySQL is a relational database "
                "management system."
            ),
            metadata={"topic": "MySQL"},
        ),
    ]

    storage.save(documents)

    search_service = SearchService(
        vector_storage=storage
    )

    context_builder = RAGContextBuilder(
        search_service=search_service
    )

    if llm_provider is None:
        service = RAGService(
            context_builder=context_builder
        )
    else:
        service = RAGService(
            context_builder=context_builder,
            llm_provider=llm_provider,
        )

    return service


def test_rag_service_generates_answer():
    """The RAG service should generate a non-empty answer."""

    service = create_rag_service(
        collection_name="test_rag_generates_answer",
        llm_provider=MockLLMProvider(),
    )

    result = service.answer(
        query="What is Python?",
        n_results=2,
    )

    assert isinstance(result, dict)
    assert result["query"] == "What is Python?"
    assert isinstance(result["answer"], str)
    assert result["answer"] != ""


def test_rag_service_includes_retrieved_context():
    """The answer result should include retrieved context."""

    service = create_rag_service(
        collection_name="test_rag_includes_context",
        llm_provider=MockLLMProvider(),
    )

    result = service.answer(
        query="What is Python?",
        n_results=2,
    )

    assert "context" in result
    assert result["context"] is not None


def test_rag_service_includes_sources():
    """The answer result should include source information."""

    service = create_rag_service(
        collection_name="test_rag_includes_sources",
        llm_provider=MockLLMProvider(),
    )

    result = service.answer(
        query="Explain Python",
        n_results=2,
    )

    assert "sources" in result
    assert isinstance(result["sources"], list)


def test_rag_service_includes_result_count():
    """The answer result should report the retrieval count."""

    service = create_rag_service(
        collection_name="test_rag_result_count",
        llm_provider=MockLLMProvider(),
    )

    result = service.answer(
        query="Explain Python",
        n_results=2,
    )

    assert "result_count" in result
    assert isinstance(result["result_count"], int)
    assert result["result_count"] >= 0


def test_rag_service_rejects_empty_query():
    """An empty query should raise ValueError."""

    service = create_rag_service(
        collection_name="test_rag_empty_query",
        llm_provider=MockLLMProvider(),
    )

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        service.answer(query="   ")


def test_rag_service_rejects_non_string_query():
    """A query must be a string."""

    service = create_rag_service(
        collection_name="test_rag_invalid_query",
        llm_provider=MockLLMProvider(),
    )

    with pytest.raises(
        TypeError,
        match="query must be a string",
    ):
        service.answer(query=123)


def test_rag_service_rejects_invalid_n_results():
    """The number of results must be positive."""

    service = create_rag_service(
        collection_name="test_rag_invalid_results",
        llm_provider=MockLLMProvider(),
    )

    with pytest.raises(ValueError):
        service.answer(
            query="What is Python?",
            n_results=0,
        )


def test_rag_service_rejects_non_integer_n_results():
    """The number of results must be an integer."""

    service = create_rag_service(
        collection_name="test_rag_non_integer_results",
        llm_provider=MockLLMProvider(),
    )

    with pytest.raises(TypeError):
        service.answer(
            query="What is Python?",
            n_results="two",
        )


def test_rag_service_uses_configured_llm_provider():
    """
    RAGService should automatically use the provider
    configured in application settings.
    """

    service = create_rag_service(
        collection_name="test_rag_configured_llm"
    )

    assert service.llm_provider is not None
    assert isinstance(
        service.llm_provider,
        MockLLMProvider,
    )

    result = service.answer(
        query="What is Python?",
        n_results=2,
    )

    assert result["query"] == "What is Python?"
    assert isinstance(result["answer"], str)
    assert result["answer"] != ""


def test_rag_service_uses_injected_llm_provider():
    """
    An explicitly supplied provider should be used.
    """

    mock_provider = MockLLMProvider()

    service = create_rag_service(
        collection_name="test_rag_injected_llm",
        llm_provider=mock_provider,
    )

    assert service.llm_provider is mock_provider


def test_rag_service_rejects_missing_provider_configuration(
    monkeypatch,
):
    """
    An invalid configured provider should not silently
    fall back to the mock provider.
    """

    from app.config.settings import settings

    monkeypatch.setattr(
        settings,
        "llm_provider",
        "unsupported_provider",
    )

    storage = VectorStorage(
        collection_name="test_rag_invalid_provider_config"
    )

    context_builder = RAGContextBuilder(
        search_service=SearchService(
            vector_storage=storage
        )
    )

    with pytest.raises(ValueError):
        RAGService(
            context_builder=context_builder
        )