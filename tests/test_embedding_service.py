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

def test_embedding_service_requires_provider_for_embedding():

    service = EmbeddingService()

    with pytest.raises(RuntimeError):

        service.embed(
            ["Hello world"]
        )


def test_embedding_service_rejects_invalid_embedding_input():

    service = EmbeddingService()

    with pytest.raises(TypeError):

        service.embed(
            "Hello world"
        )


def test_embedding_service_empty_embedding_input():

    service = EmbeddingService()

    assert (
        service.embed([])
        == []
    )


class MockEmbeddingProvider:

    def embed(
        self,
        texts,
    ):

        return [
            [1.0, 2.0, 3.0]
            for _ in texts
        ]


def test_embedding_service_uses_provider():

    provider = MockEmbeddingProvider()

    service = EmbeddingService(
        provider=provider
    )

    result = service.embed(
        [
            "  Hello world  ",
            "Python",
        ]
    )

    assert result == [
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    ]