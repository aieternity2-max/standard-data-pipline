from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract interface for Large Language Model providers.

    Concrete providers can implement this interface for
    OpenAI, local models, Hugging Face, or other LLM services.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response from the supplied prompt.

        Parameters
        ----------
        prompt:
            Prompt sent to the language model.

        Returns
        -------
        str
            Generated response.
        """

        raise NotImplementedError