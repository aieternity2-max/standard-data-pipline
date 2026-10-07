from app.embeddings.base import EmbeddingProvider


class EmbeddingProviderFactory:
    """
    Factory for selecting embedding providers.

    External providers are intentionally not implemented yet.
    This factory establishes the extension point for future
    OpenAI, Hugging Face, and local embedding providers.
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

        provider_name = provider_name.strip().lower()

        if not provider_name:
            raise ValueError(
                "provider_name cannot be empty"
            )

        if provider_name not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported embedding provider: "
                f"{provider_name}"
            )

        return provider_name