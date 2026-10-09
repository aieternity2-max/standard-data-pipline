import pytest

from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.provider_factory import LLMProviderFactory


def test_factory_creates_mock_provider():
    """The factory should create a mock LLM provider."""

    provider = LLMProviderFactory.create("mock")

    assert isinstance(provider, LLMProvider)
    assert isinstance(provider, MockLLMProvider)


def test_factory_normalizes_provider_name():
    """Provider names should be normalized."""

    provider = LLMProviderFactory.create(" MOCK ")

    assert isinstance(provider, MockLLMProvider)


def test_factory_rejects_unsupported_provider():
    """Unsupported provider names should raise ValueError."""

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider",
    ):
        LLMProviderFactory.create("unsupported_provider")


def test_factory_rejects_non_string_provider_name():
    """Provider names must be strings."""

    with pytest.raises(
        TypeError,
        match="provider_name must be a string",
    ):
        LLMProviderFactory.create(None)


def test_factory_rejects_empty_provider_name():
    """Empty provider names should raise ValueError."""

    with pytest.raises(
        ValueError,
        match="provider_name cannot be empty",
    ):
        LLMProviderFactory.create("   ")


def test_factory_validates_provider_name():
    """The validation method should normalize valid names."""

    provider_name = LLMProviderFactory.validate_provider(
        " MOCK "
    )

    assert provider_name == "mock"


def test_factory_accepts_openai_as_supported_provider():
    """
    OpenAI is a supported provider.

    This test checks the factory's provider-name validation
    without requiring an OpenAI API key.
    """

    provider_name = LLMProviderFactory.validate_provider(
        "openai"
    )

    assert provider_name == "openai"