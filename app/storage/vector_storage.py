from app.models.document import Document

import chromadb


class VectorStorage:
    """
    Storage interface for vector databases.

    Uses persistent ChromaDB for local vector storage.
    """

    def __init__(
        self,
        collection_name: str = "documents",
    ):
        """
        Initialize vector storage.

        Creates or loads a persistent ChromaDB collection.
        """

        if not collection_name:
            raise ValueError(
                "collection_name is required"
            )

        self.client = chromadb.PersistentClient(
            path="data/chroma"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name
            )
        )

    def save(
        self,
        documents: list[Document],
    ) -> int:
        """
        Store documents in the vector database.

        Returns the number of documents saved.
        """

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

        if not documents:
            return 0

        ids = []
        contents = []
        metadatas = []

        for document in documents:

            ids.append(document.id)

            contents.append(
                document.content
            )

            metadata = dict(
                document.metadata or {}
            )

            metadata["source"] = document.source
            metadata["source_type"] = (
                document.source_type
            )

            metadatas.append(metadata)

        self.collection.upsert(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
        )

        return len(documents)

    def count(self) -> int:
        """
        Return the number of documents
        currently stored.
        """

        return self.collection.count()

    def search(
        self,
        query: str,
        n_results: int = 5,
    ):
        """
        Search for documents similar to the query.
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