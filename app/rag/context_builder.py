from app.search.search_service import SearchService


class RAGContextBuilder:
    """
    Builds retrieval context for Retrieval-Augmented Generation (RAG).

    Flow:

        User Query
            ↓
        SearchService
            ↓
        Retrieved Documents
            ↓
        Context Builder
            ↓
        Formatted RAG Context
    """

    def __init__(
        self,
        search_service: SearchService | None = None,
    ):
        """
        Initialize the RAG context builder.

        Parameters
        ----------
        search_service:
            Optional SearchService instance.

            If not provided, a default SearchService
            is created.
        """

        self.search_service = (
            search_service
            if search_service is not None
            else SearchService()
        )

    def build(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict:
        """
        Retrieve relevant documents and build RAG context.

        Parameters
        ----------
        query:
            User's natural-language question.

        n_results:
            Number of relevant chunks to retrieve.

        Returns
        -------
        dict
            Structured RAG context containing the query,
            retrieved documents, and formatted context.
        """

        # -----------------------------------------
        # Validate query
        # -----------------------------------------

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "query must be a string"
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "query cannot be empty"
            )

        # -----------------------------------------
        # Validate result count
        # -----------------------------------------

        if not isinstance(
            n_results,
            int,
        ):
            raise TypeError(
                "n_results must be an integer"
            )

        if n_results <= 0:
            raise ValueError(
                "n_results must be greater than 0"
            )

        # -----------------------------------------
        # Retrieve relevant documents
        # -----------------------------------------

        results = self.search_service.search(
            query=query,
            n_results=n_results,
        )

        # -----------------------------------------
        # Extract result fields
        # -----------------------------------------

        ids = results.get(
            "ids",
            [[]],
        )

        documents = results.get(
            "documents",
            [[]],
        )

        metadatas = results.get(
            "metadatas",
            [[]],
        )

        distances = results.get(
            "distances",
            [[]],
        )

        retrieved_ids = (
            ids[0]
            if ids
            else []
        )

        retrieved_documents = (
            documents[0]
            if documents
            else []
        )

        retrieved_metadatas = (
            metadatas[0]
            if metadatas
            else []
        )

        retrieved_distances = (
            distances[0]
            if distances
            else []
        )

        # -----------------------------------------
        # Build structured sources
        # -----------------------------------------

        sources = []

        for index, content in enumerate(
            retrieved_documents
        ):

            source = {
                "id": (
                    retrieved_ids[index]
                    if index < len(retrieved_ids)
                    else None
                ),
                "content": content,
                "metadata": (
                    retrieved_metadatas[index]
                    if index < len(
                        retrieved_metadatas
                    )
                    else {}
                ),
                "distance": (
                    retrieved_distances[index]
                    if index < len(
                        retrieved_distances
                    )
                    else None
                ),
            }

            sources.append(source)

        # -----------------------------------------
        # Build formatted context
        # -----------------------------------------

        context_parts = []

        for index, source in enumerate(
            sources,
            start=1,
        ):

            context_parts.append(
                (
                    f"[Source {index}]\n"
                    f"{source['content']}"
                )
            )

        context = "\n\n".join(
            context_parts
        )

        # -----------------------------------------
        # Return RAG context
        # -----------------------------------------

        return {
            "query": query,
            "context": context,
            "sources": sources,
            "result_count": len(sources),
        }