from app.embeddings.base import EmbeddingProvider
from app.embeddings.chromadb_provider import (
    ChromaDBEmbeddingProvider,
)


class EmbeddingProviderFactory:
    """
    Factory for selecting embedding providers.

    ChromaDB is currently implemented.

    External providers such as OpenAI,
    Hugging Face, and local models remain
    extension points for future implementation.
    """

    SUPPORTED_PROVIDERS = {
        "chromadb",
        "openai",
        "huggingface",
        "local",
    }

    @classmethod
    def validate_provider(
        cls,
        provider_name: str,
    ) -> str:
        """
        Validate and normalize an embedding provider name.
        """

        if not isinstance(
            provider_name,
            str,
        ):
            raise TypeError(
                "provider_name must be a string"
            )

        provider_name = (
            provider_name.strip().lower()
        )

        if not provider_name:
            raise ValueError(
                "provider_name cannot be empty"
            )

        if (
            provider_name
            not in cls.SUPPORTED_PROVIDERS
        ):
            raise ValueError(
                f"Unsupported embedding provider: "
                f"{provider_name}"
            )

        return provider_name

    @classmethod
    def create(
        cls,
        provider_name: str,
    ) -> EmbeddingProvider:
        """
        Create the configured embedding provider.

        Currently supported:
        - chromadb

        Future providers:
        - openai
        - huggingface
        - local
        """

        provider_name = (
            cls.validate_provider(
                provider_name
            )
        )

        if provider_name == "chromadb":
            return ChromaDBEmbeddingProvider()

        raise NotImplementedError(
            f"Embedding provider '{provider_name}' "
            f"is registered but not implemented yet"
        )