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


def test_vector_storage_with_explicit_embeddings():

    documents = [
        Document(
            id="explicit-embedding-1",
            source="sample.txt",
            source_type="txt",
            content="Hello world",
            metadata={},
        ),
        Document(
            id="explicit-embedding-2",
            source="sample.txt",
            source_type="txt",
            content="Python programming",
            metadata={},
        ),
    ]

    embeddings = [
        [0.1] * 384,
        [0.2] * 384,
    ]

    storage = VectorStorage(
        collection_name="test_explicit_embeddings"
    )

    saved_count = storage.save(
        documents,
        embeddings=embeddings,
    )

    assert saved_count == 2

    assert storage.count() == 2


def test_vector_storage_rejects_embedding_count_mismatch():

    documents = [
        Document(
            id="mismatch-1",
            source="sample.txt",
            source_type="txt",
            content="Hello world",
            metadata={},
        ),
        Document(
            id="mismatch-2",
            source="sample.txt",
            source_type="txt",
            content="Python",
            metadata={},
        ),
    ]

    embeddings = [
        [0.1] * 384,
    ]

    storage = VectorStorage(
        collection_name="test_embedding_mismatch"
    )

    try:

        storage.save(
            documents,
            embeddings=embeddings,
        )

        assert False

    except ValueError:

        assert True


def test_vector_storage_rejects_invalid_embeddings():

    documents = [
        Document(
            id="invalid-embedding-1",
            source="sample.txt",
            source_type="txt",
            content="Hello world",
            metadata={},
        ),
    ]

    storage = VectorStorage(
        collection_name="test_invalid_embeddings"
    )

    try:

        storage.save(
            documents,
            embeddings=[
                ["invalid"]
            ],
        )

        assert False

    except TypeError:

        assert True