import pytest

from app.embeddings.provider_factory import (
    EmbeddingProviderFactory,
)


def test_factory_accepts_chromadb():

    result = (
        EmbeddingProviderFactory.validate_provider(
            "chromadb"
        )
    )

    assert result == "chromadb"


def test_factory_normalizes_provider_name():

    result = (
        EmbeddingProviderFactory.validate_provider(
            "  ChRoMaDb  "
        )
    )

    assert result == "chromadb"


def test_factory_accepts_future_providers():

    assert (
        EmbeddingProviderFactory.validate_provider(
            "openai"
        )
        == "openai"
    )

    assert (
        EmbeddingProviderFactory.validate_provider(
            "huggingface"
        )
        == "huggingface"
    )

    assert (
        EmbeddingProviderFactory.validate_provider(
            "local"
        )
        == "local"
    )


def test_factory_rejects_unknown_provider():

    with pytest.raises(ValueError):

        EmbeddingProviderFactory.validate_provider(
            "unknown"
        )


def test_factory_rejects_empty_provider():

    with pytest.raises(ValueError):

        EmbeddingProviderFactory.validate_provider(
            "   "
        )


def test_factory_rejects_non_string_provider():

    with pytest.raises(TypeError):

        EmbeddingProviderFactory.validate_provider(
            123
        )