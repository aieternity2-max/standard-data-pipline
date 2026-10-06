class EmbeddingService:
    """
    Service layer for document embedding operations.

    ChromaDB currently handles the actual embedding generation.
    This service provides a clean abstraction so an external
    embedding model can be introduced later without changing
    the ingestion pipeline.
    """

    def __init__(self):
        """
        Initialize the embedding service.
        """
        pass

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

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty"
            )

        return text