import pytest

from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider


def test_llm_provider_is_abstract():

    with pytest.raises(TypeError):

        LLMProvider()


def test_mock_llm_provider_generates_response():

    provider = MockLLMProvider()

    result = provider.generate(
        "What is Python?"
    )

    assert isinstance(
        result,
        str,
    )

    assert (
        result
        == "Mock LLM response generated "
        "from the supplied context."
    )


def test_mock_llm_provider_rejects_non_string_prompt():

    provider = MockLLMProvider()

    with pytest.raises(TypeError):

        provider.generate(
            123
        )


def test_mock_llm_provider_rejects_empty_prompt():

    provider = MockLLMProvider()

    with pytest.raises(ValueError):

        provider.generate(
            "   "
        )