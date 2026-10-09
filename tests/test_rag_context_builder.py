import pytest

from app.models.document import Document
from app.rag.context_builder import (
    RAGContextBuilder,
)
from app.search.search_service import (
    SearchService,
)
from app.storage.vector_storage import (
    VectorStorage,
)


def test_rag_context_builder():

    storage = VectorStorage(
        collection_name="test_rag_context_builder"
    )

    documents = [
        Document(
            id="rag-1",
            source="python.txt",
            source_type="txt",
            content=(
                "Python is a programming language"
            ),
            metadata={
                "topic": "python",
            },
        ),
        Document(
            id="rag-2",
            source="mysql.txt",
            source_type="txt",
            content=(
                "MySQL is a relational database"
            ),
            metadata={
                "topic": "database",
            },
        ),
    ]

    storage.save(documents)

    search_service = SearchService(
        vector_storage=storage
    )

    builder = RAGContextBuilder(
        search_service=search_service
    )

    result = builder.build(
        query="Python programming",
        n_results=1,
    )

    assert result["query"] == (
        "Python programming"
    )

    assert result["result_count"] == 1

    assert len(
        result["sources"]
    ) == 1

    assert (
        result["sources"][0]["id"]
        == "rag-1"
    )

    assert (
        "Python is a programming language"
        in result["context"]
    )


def test_rag_context_builder_contains_metadata():

    storage = VectorStorage(
        collection_name="test_rag_metadata"
    )

    document = Document(
        id="metadata-1",
        source="sample.txt",
        source_type="txt",
        content="Machine learning uses data",
        metadata={
            "topic": "machine-learning",
        },
    )

    storage.save([document])

    service = SearchService(
        vector_storage=storage
    )

    builder = RAGContextBuilder(
        search_service=service
    )

    result = builder.build(
        query="machine learning",
        n_results=1,
    )

    assert (
        result["sources"][0]["metadata"]
        ["topic"]
        == "machine-learning"
    )


def test_rag_context_builder_rejects_empty_query():

    builder = RAGContextBuilder()

    with pytest.raises(ValueError):

        builder.build(
            query="   "
        )


def test_rag_context_builder_rejects_non_string_query():

    builder = RAGContextBuilder()

    with pytest.raises(TypeError):

        builder.build(
            query=123
        )


def test_rag_context_builder_rejects_invalid_n_results():

    builder = RAGContextBuilder()

    with pytest.raises(ValueError):

        builder.build(
            query="Python",
            n_results=0,
        )


def test_rag_context_builder_rejects_non_integer_n_results():

    builder = RAGContextBuilder()

    with pytest.raises(TypeError):

        builder.build(
            query="Python",
            n_results="5",
        )