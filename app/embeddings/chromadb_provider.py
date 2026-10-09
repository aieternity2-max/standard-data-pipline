from chromadb.utils.embedding_functions import (
    DefaultEmbeddingFunction,
)

from app.embeddings.base import EmbeddingProvider


class ChromaDBEmbeddingProvider(
    EmbeddingProvider
):
    """
    Embedding provider using ChromaDB's
    built-in default embedding function.

    ChromaDB currently generates local
    384-dimensional embeddings using its
    default embedding implementation.

    This provider only handles embedding generation.
    Vector persistence remains the responsibility
    of VectorStorage.
    """

    def __init__(self):
        self.embedding_function = (
            DefaultEmbeddingFunction()
        )

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

        for text in texts:

            if not isinstance(
                text,
                str,
            ):
                raise TypeError(
                    "all texts must be strings"
                )

        embeddings = (
            self.embedding_function(
                texts
            )
        )

        return [
            vector.tolist()
            for vector in embeddings
        ]