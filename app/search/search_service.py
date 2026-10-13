"""Application service for semantic document search."""

from app.storage.vector_storage import VectorStorage


class SearchService:
    """Provide a stable interface for semantic document search."""

    def __init__(self, vector_storage: VectorStorage | None = None):
        self.vector_storage = (
            vector_storage
            if vector_storage is not None
            else VectorStorage()
        )

    def search(self, query: str, n_results: int = 5) -> dict:
        """Search for documents similar to the supplied query."""

        if not isinstance(query, str):
            raise TypeError("query must be a string")

        query = query.strip()

        if not query:
            raise ValueError("query cannot be empty")

        if not isinstance(n_results, int):
            raise TypeError("n_results must be an integer")

        if n_results <= 0:
            raise ValueError("n_results must be greater than 0")

        return self.vector_storage.search(
            query=query,
            n_results=n_results,
        )