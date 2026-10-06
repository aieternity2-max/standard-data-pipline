from app.embeddings.base import EmbeddingProvider


class EmbeddingService:
    """
    Service layer for document embedding operations.

    The service validates and prepares text before it is
    passed to an embedding provider.

    An actual embedding provider can be introduced later
    without changing the service interface.
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

            The provider is intentionally optional because
            ChromaDB currently handles embedding generation
            internally.
        """

        self.provider = provider

    def prepare_text(
        self,
        text: str,
    ) -> str:
        """
        Validate and prepare text before embedding.

        Parameters
        ----------
        text:
            Text that will be embedded.

        Returns
        -------
        str
            Clean text ready for embedding.
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

        Parameters
        ----------
        texts:
            Texts to embed.

        Returns
        -------
        list[list[float]]
            Generated embedding vectors.
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

        if self.provider is None:
            raise RuntimeError(
                "No embedding provider is configured"
            )

        return self.provider.embed(
            prepared_texts
        )