import pytest

from app.embeddings.provider_factory import (
    EmbeddingProviderFactory,
)

from app.embeddings.chromadb_provider import (
    ChromaDBEmbeddingProvider,
)


def test_factory_creates_chromadb_provider():

    provider = (
        EmbeddingProviderFactory.create(
            "chromadb"
        )
    )

    assert isinstance(
        provider,
        ChromaDBEmbeddingProvider,
    )


def test_factory_rejects_unimplemented_provider():

    with pytest.raises(NotImplementedError):

        EmbeddingProviderFactory.create(
            "openai"
        )