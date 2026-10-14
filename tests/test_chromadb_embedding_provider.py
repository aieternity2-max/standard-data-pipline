import pytest

from app.embeddings.base import EmbeddingProvider
from app.embeddings.chromadb_provider import ChromaDBEmbeddingProvider


def test_chromadb_provider_instance():
    provider = ChromaDBEmbeddingProvider()
    assert isinstance(provider, EmbeddingProvider)
    assert isinstance(provider, ChromaDBEmbeddingProvider)


def test_chromadb_provider_empty_input():
    provider = ChromaDBEmbeddingProvider()
    assert provider.embed([]) == []


def test_chromadb_provider_rejects_non_list():
    provider = ChromaDBEmbeddingProvider()
    with pytest.raises(TypeError, match="texts must be a list"):
        provider.embed("hello world")


def test_chromadb_provider_rejects_non_string_elements():
    provider = ChromaDBEmbeddingProvider()
    with pytest.raises(TypeError, match="all texts must be strings"):
        provider.embed(["valid text", 123])


def test_chromadb_provider_generates_embeddings():
    provider = ChromaDBEmbeddingProvider()
    result = provider.embed(["Hello world", "Data pipeline"])

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert len(result[0]) == 384
    assert isinstance(result[0][0], float)