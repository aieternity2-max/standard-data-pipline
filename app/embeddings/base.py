from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract interface for embedding providers.

    Implementations can use ChromaDB, external APIs,
    local embedding models, or other providers.
    """

    @abstractmethod
    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Parameters
        ----------
        texts:
            Texts to embed.

        Returns
        -------
        list[list[float]]
            Embedding vectors.
        """
        raise NotImplementedError