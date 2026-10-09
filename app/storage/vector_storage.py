import chromadb

from app.config.settings import settings
from app.models.document import Document


class VectorStorage:
    """
    Storage interface for ChromaDB vector storage.

    Supports:
    - Normal document storage where ChromaDB generates embeddings.
    - Explicit embedding storage where embeddings are generated
      by EmbeddingService / a configured embedding provider.
    """

    def __init__(
        self,
        collection_name: str | None = None,
    ):
        """
        Initialize vector storage.

        Parameters
        ----------
        collection_name:
            Optional ChromaDB collection name.
            If not provided, the configured default is used.
        """

        collection_name = (
            collection_name
            or settings.chroma_collection
        )

        if not collection_name:
            raise ValueError(
                "collection_name is required"
            )

        self.client = chromadb.PersistentClient(
            path=settings.chroma_path
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name
            )
        )

    def save(
        self,
        documents: list[Document],
        embeddings: list[list[float]] | None = None,
    ) -> int:
        """
        Store documents in ChromaDB.

        If embeddings are supplied, they are stored explicitly.

        If embeddings are not supplied, ChromaDB generates
        embeddings internally using its configured embedding
        function.

        Parameters
        ----------
        documents:
            Documents to store.

        embeddings:
            Optional embedding vectors corresponding to each
            document.

        Returns
        -------
        int
            Number of documents saved.
        """

        # -----------------------------------------
        # Validate documents
        # -----------------------------------------

        if not isinstance(
            documents,
            list,
        ):
            raise TypeError(
                "documents must be a list"
            )

        for document in documents:

            if not isinstance(
                document,
                Document,
            ):
                raise TypeError(
                    "All items must be Document instances"
                )

        # -----------------------------------------
        # Empty input
        # -----------------------------------------

        if not documents:
            return 0

        # -----------------------------------------
        # Validate embeddings
        # -----------------------------------------

        if embeddings is not None:

            if not isinstance(
                embeddings,
                list,
            ):
                raise TypeError(
                    "embeddings must be a list"
                )

            if len(embeddings) != len(documents):

                raise ValueError(
                    "Number of embeddings must match "
                    "number of documents"
                )

            for embedding in embeddings:

                if not isinstance(
                    embedding,
                    list,
                ):
                    raise TypeError(
                        "Each embedding must be a list"
                    )

                if not embedding:

                    raise ValueError(
                        "Embedding vectors cannot be empty"
                    )

                for value in embedding:

                    if not isinstance(
                        value,
                        (int, float),
                    ):
                        raise TypeError(
                            "Embedding values must be numeric"
                        )

        # -----------------------------------------
        # Prepare ChromaDB data
        # -----------------------------------------

        ids = []

        contents = []

        metadatas = []

        for document in documents:

            ids.append(
                document.id
            )

            contents.append(
                document.content
            )

            metadata = dict(
                document.metadata or {}
            )

            metadata["source"] = (
                document.source
            )

            metadata["source_type"] = (
                document.source_type
            )

            metadatas.append(
                metadata
            )

        # -----------------------------------------
        # Store documents
        # -----------------------------------------

        if embeddings is None:

            # ChromaDB generates embeddings internally.
            self.collection.upsert(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
            )

        else:

            # Explicit embeddings generated by the
            # configured EmbeddingProvider.
            self.collection.upsert(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        return len(documents)

    def count(self) -> int:
        """
        Return the number of documents currently stored.
        """

        return self.collection.count()

    def search(
        self,
        query: str,
        n_results: int = 5,
    ):
        """
        Search for documents similar to the query.

        ChromaDB generates the query embedding using its
        configured embedding function.

        Parameters
        ----------
        query:
            Natural-language search query.

        n_results:
            Maximum number of results.

        Returns
        -------
        dict
            ChromaDB query result.
        """

        if not query:
            raise ValueError(
                "query is required"
            )

        if n_results <= 0:
            raise ValueError(
                "n_results must be greater than 0"
            )

        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )