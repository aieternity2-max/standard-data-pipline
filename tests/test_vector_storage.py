from app.models.document import Document

from app.storage.vector_storage import (
    VectorStorage,
)


def test_vector_storage_search():

    storage = VectorStorage(
        collection_name="test_search"
    )

    documents = [
        Document(
            id="doc-search-1",
            source="sample.txt",
            source_type="txt",
            content="Python is a programming language",
            metadata={},
        ),
        Document(
            id="doc-search-2",
            source="sample.txt",
            source_type="txt",
            content="MySQL is a relational database",
            metadata={},
        ),
    ]

    saved_count = storage.save(
        documents
    )

    assert saved_count == 2

    results = storage.search(
        query="programming language",
        n_results=1,
    )

    assert results is not None
    assert "ids" in results
    assert len(results["ids"]) > 0

    assert (
        results["ids"][0][0]
        == "doc-search-1"
    )


def test_vector_storage():

    documents = [
        Document(
            id="vector-doc-1",
            source="sample.txt",
            source_type="txt",
            content="Hello world",
            metadata={},
        ),
        Document(
            id="vector-doc-2",
            source="sample.txt",
            source_type="txt",
            content="This is a test document",
            metadata={},
        ),
    ]

    storage = VectorStorage(
        collection_name="test_documents"
    )

    saved_count = storage.save(
        documents
    )

    assert saved_count == 2
    assert storage.count() == 2

    results = storage.search(
        "Hello world",
        n_results=1,
    )

    assert len(results["documents"]) == 1

    assert (
        results["documents"][0][0]
        == "Hello world"
    )


def test_vector_storage_persistence():

    documents = [
        Document(
            id="persistent-doc-1",
            source="persistent.txt",
            source_type="txt",
            content="This document must persist",
            metadata={},
        )
    ]

    storage = VectorStorage(
        collection_name="test_persistence"
    )

    saved_count = storage.save(
        documents
    )

    assert saved_count == 1
    assert storage.count() == 1

    new_storage = VectorStorage(
        collection_name="test_persistence"
    )

    assert new_storage.count() == 1

    results = new_storage.search(
        "document must persist",
        n_results=1,
    )

    assert (
        results["ids"][0][0]
        == "persistent-doc-1"
    )