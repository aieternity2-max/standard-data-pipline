from app.models.document import Document


class VectorStorage:
    """
    Storage interface for vector databases.

    The actual vector database integration will be
    added later.
    """

    def save(
        self,
        documents: list[Document],
    ) -> int:
        """
        Process documents for vector storage.

        Returns the number of documents processed.
        """

        if not isinstance(documents, list):
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

        return len(documents)