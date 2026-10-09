import pytest

from app.models.document import Document
from app.search.search_service import SearchService
from app.storage.vector_storage import VectorStorage


def test_search_service_returns_results():

    storage = VectorStorage(
        collection_name="test_search_service"
    )

    documents = [
        Document(
            id="search-service-1",
            source="sample.txt",
            source_type="txt",
            content="Python is a programming language",
            metadata={
                "category": "programming",
            },
        ),
        Document(
            id="search-service-2",
            source="sample.txt",
            source_type="txt",
            content="MySQL is a relational database",
            metadata={
                "category": "database",
            },
        ),
    ]

    storage.save(documents)

    service = SearchService(
        vector_storage=storage
    )

    results = service.search(
        query="programming language",
        n_results=1,
    )

    assert results is not None

    assert "ids" in results

    assert (
        results["ids"][0][0]
        == "search-service-1"
    )


def test_search_service_respects_n_results():

    storage = VectorStorage(
        collection_name="test_search_service_limit"
    )

    documents = [
        Document(
            id="limit-1",
            source="sample.txt",
            source_type="txt",
            content="Python programming",
            metadata={},
        ),
        Document(
            id="limit-2",
            source="sample.txt",
            source_type="txt",
            content="Python development",
            metadata={},
        ),
    ]

    storage.save(documents)

    service = SearchService(
        vector_storage=storage
    )

    results = service.search(
        query="Python",
        n_results=1,
    )

    assert len(
        results["ids"][0]
    ) == 1


def test_search_service_rejects_non_string_query():

    service = SearchService()

    with pytest.raises(TypeError):

        service.search(
            query=123
        )


def test_search_service_rejects_empty_query():

    service = SearchService()

    with pytest.raises(ValueError):

        service.search(
            query="   "
        )


def test_search_service_rejects_invalid_n_results():

    service = SearchService()

    with pytest.raises(ValueError):

        service.search(
            query="Python",
            n_results=0,
        )


def test_search_service_rejects_non_integer_n_results():

    service = SearchService()

    with pytest.raises(TypeError):

        service.search(
            query="Python",
            n_results="5",
        )