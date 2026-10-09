from openai import OpenAI

from app.config.settings import settings
from app.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """
    LLM provider implementation using OpenAI.

    This provider communicates with the OpenAI Responses API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """
        Initialize the OpenAI provider.

        Parameters
        ----------
        api_key:
            OpenAI API key.

        model:
            OpenAI model name.
        """

        self.api_key = (
            api_key
            if api_key is not None
            else settings.openai_api_key
        )

        self.model = (
            model
            if model is not None
            else settings.openai_model
        )

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is not configured"
            )

        if not isinstance(
            self.model,
            str,
        ):
            raise TypeError(
                "model must be a string"
            )

        self.model = self.model.strip()

        if not self.model:
            raise ValueError(
                "model cannot be empty"
            )

        self.client = OpenAI(
            api_key=self.api_key
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response using OpenAI.

        Parameters
        ----------
        prompt:
            Prompt supplied to the model.

        Returns
        -------
        str
            Generated response.
        """

        if not isinstance(
            prompt,
            str,
        ):
            raise TypeError(
                "prompt must be a string"
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "prompt cannot be empty"
            )

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text