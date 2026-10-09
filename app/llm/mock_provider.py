from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Deterministic LLM provider used for testing.

    This provider does not call an external model.
    """

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Return a deterministic response for testing.
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

        return (
            "Mock LLM response generated "
            "from the supplied context."
        )