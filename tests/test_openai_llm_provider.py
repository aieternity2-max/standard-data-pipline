from unittest.mock import MagicMock
import pytest

from app.llm.base import LLMProvider
from app.llm.openai_provider import OpenAILLMProvider


def test_openai_provider_missing_api_key_raises(monkeypatch):
    monkeypatch.setattr("app.llm.openai_provider.settings.openai_api_key", None)
    with pytest.raises(ValueError, match="OpenAI API key is not configured"):
        OpenAILLMProvider(api_key=None)


def test_openai_provider_invalid_model_type_raises():
    with pytest.raises(TypeError, match="model must be a string"):
        OpenAILLMProvider(api_key="sk-testkey", model=123)


def test_openai_provider_empty_model_raises():
    with pytest.raises(ValueError, match="model cannot be empty"):
        OpenAILLMProvider(api_key="sk-testkey", model="   ")


def test_openai_provider_init_success(monkeypatch):
    mock_client = MagicMock()
    monkeypatch.setattr("app.llm.openai_provider.OpenAI", lambda api_key: mock_client)

    provider = OpenAILLMProvider(api_key="sk-testkey", model="gpt-4o")
    assert isinstance(provider, LLMProvider)
    assert provider.api_key == "sk-testkey"
    assert provider.model == "gpt-4o"
    assert provider.client == mock_client


def test_openai_provider_generate_success(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = "Generated AI response."
    mock_client.responses.create.return_value = mock_response

    monkeypatch.setattr("app.llm.openai_provider.OpenAI", lambda api_key: mock_client)

    provider = OpenAILLMProvider(api_key="sk-testkey", model="gpt-4o")
    result = provider.generate("Summarize this document")

    assert result == "Generated AI response."
    mock_client.responses.create.assert_called_once_with(
        model="gpt-4o",
        input="Summarize this document",
    )


def test_openai_provider_generate_rejects_non_string():
    mock_client = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.llm.openai_provider.OpenAI", lambda api_key: mock_client)
        provider = OpenAILLMProvider(api_key="sk-testkey", model="gpt-4o")

        with pytest.raises(TypeError, match="prompt must be a string"):
            provider.generate(12345)


def test_openai_provider_generate_rejects_empty_prompt():
    mock_client = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.llm.openai_provider.OpenAI", lambda api_key: mock_client)
        provider = OpenAILLMProvider(api_key="sk-testkey", model="gpt-4o")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            provider.generate("   \n\t  ")
