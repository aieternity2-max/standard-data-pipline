from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAILLMProvider


class LLMProviderFactory:
    """
    Factory for creating LLM providers.
    """

    SUPPORTED_PROVIDERS = {
        "mock",
        "openai",
    }

    @classmethod
    def validate_provider(
        cls,
        provider_name: str,
    ) -> str:
        """
        Validate and normalize provider name.
        """
        if not isinstance(provider_name, str):
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

        if provider_name not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported LLM provider: "
                f"{provider_name}"
            )

        return provider_name

    @classmethod
    def create(
        cls,
        provider_name: str,
    ) -> LLMProvider:
        """
        Create an LLM provider.
        """

        provider_name = cls.validate_provider(
            provider_name
        )

        if provider_name == "mock":
            return MockLLMProvider()

        if provider_name == "openai":
            return OpenAILLMProvider()

        raise NotImplementedError(
            f"LLM provider '{provider_name}' "
            "is not implemented"
        )