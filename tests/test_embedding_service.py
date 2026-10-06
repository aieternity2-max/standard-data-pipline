import pytest

from app.embeddings.embedding_service import (
    EmbeddingService,
)


def test_embedding_service_prepare_text():

    service = EmbeddingService()

    result = service.prepare_text(
        "  Hello world  "
    )

    assert result == "Hello world"


def test_embedding_service_rejects_non_string():

    service = EmbeddingService()

    with pytest.raises(TypeError):

        service.prepare_text(
            123
        )


def test_embedding_service_rejects_empty_text():

    service = EmbeddingService()

    with pytest.raises(ValueError):

        service.prepare_text(
            "   "
        )