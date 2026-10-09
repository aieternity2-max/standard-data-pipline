from app.storage.vector_storage import VectorStorage


class SearchService:
    """
    Application service for semantic document search.

    This service sits above VectorStorage and provides
    validation and a stable interface for future RAG,
    Streamlit, and API consumers.
    """

    def __init__(
        self,
        vector_storage: VectorStorage | None = None,
    ):
        """
        Initialize the search service.

        Parameters
        ----------
        vector_storage:
            Optional VectorStorage instance.

            If not provided, a default VectorStorage
            instance is created.
        """

        self.vector_storage = (
            vector_storage
            if vector_storage is not None
            else VectorStorage()
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict:
        """
        Perform semantic search over indexed documents.

        Parameters
        ----------
        query:
            Natural-language search query.

        n_results:
            Maximum number of results to return.

        Returns
        -------
        dict
            Search results returned by VectorStorage.
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
        # Execute semantic search
        # -----------------------------------------

        results = self.vector_storage.search(
            query=query,
            n_results=n_results,
        )

        # -----------------------------------------
        # Return search results
        # -----------------------------------------

        return results