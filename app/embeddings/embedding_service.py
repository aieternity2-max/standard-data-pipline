from app.config.settings import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.provider_factory import (
    EmbeddingProviderFactory,
)


class EmbeddingService:
    """
    Service layer for document embedding operations.

    The service validates and prepares text before it is
    passed to an embedding provider.

    The provider is selected from application configuration
    when one is not explicitly supplied.
    """

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
    ):
        """
        Initialize the embedding service.

        Parameters
        ----------
        provider:
            Optional embedding provider.

            If provided, dependency injection is used.

            If not provided, the provider is created from
            the EMBEDDING_PROVIDER configuration.
        """

        if provider is not None:

            self.provider = provider

        else:

            self.provider = (
                EmbeddingProviderFactory.create(
                    settings.embedding_provider
                )
            )

    def prepare_text(
        self,
        text: str,
    ) -> str:
        """
        Validate and prepare text before embedding.
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text must be a string"
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty"
            )

        return text

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings using the configured provider.
        """

        if not isinstance(
            texts,
            list,
        ):
            raise TypeError(
                "texts must be a list"
            )

        if not texts:
            return []

        prepared_texts = [
            self.prepare_text(text)
            for text in texts
        ]

        return self.provider.embed(
            prepared_texts
        )