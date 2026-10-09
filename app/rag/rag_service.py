from app.config.settings import settings
from app.llm.base import LLMProvider
from app.llm.provider_factory import LLMProviderFactory
from app.rag.context_builder import RAGContextBuilder


class RAGService:
    """
    Orchestrates retrieval-augmented generation.

    Flow:
        User Query
            ↓
        RAGContextBuilder
            ↓
        Retrieved Context
            ↓
        LLMProvider
            ↓
        Answer + Sources
    """

    def __init__(
        self,
        context_builder: RAGContextBuilder | None = None,
        llm_provider: LLMProvider | None = None,
    ):
        """
        Initialize the RAG service.

        An explicitly supplied LLM provider takes priority.
        Otherwise, the provider is created from application
        configuration.
        """

        # Initialize the context builder.
        self.context_builder = (
            context_builder
            if context_builder is not None
            else RAGContextBuilder()
        )

        # Initialize the LLM provider.
        self.llm_provider = (
            llm_provider
            if llm_provider is not None
            else LLMProviderFactory.create(
                settings.llm_provider
            )
        )

    def answer(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict:
        """
        Retrieve relevant context and generate an answer.

        Returns:
            A dictionary containing:
                query
                answer
                context
                sources
                result_count
        """

        # Validate the query.
        if not isinstance(query, str):
            raise TypeError(
                "query must be a string"
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "query cannot be empty"
            )

        # Validate the number of results.
        if isinstance(n_results, bool) or not isinstance(
            n_results, int
        ):
            raise TypeError(
                "n_results must be an integer"
            )

        if n_results <= 0:
            raise ValueError(
                "n_results must be greater than 0"
            )

        # Retrieve relevant context.
        rag_context = self.context_builder.build(
            query=query,
            n_results=n_results,
        )

        context = rag_context["context"]

        # Construct the prompt.
        prompt = self._build_prompt(
            query=query,
            context=context,
        )

        # Generate the answer.
        answer = self.llm_provider.generate(
            prompt
        )

        # Return the standardized RAG response.
        return {
            "query": query,
            "answer": answer,
            "context": context,
            "sources": rag_context["sources"],
            "result_count": rag_context["result_count"],
        }

    @staticmethod
    def _build_prompt(
        query: str,
        context: str,
    ) -> str:
        """
        Construct the prompt using the retrieved context.
        """

        return (
            "Answer the user's question using "
            "only the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{query}\n\n"
            "Answer:"
        )