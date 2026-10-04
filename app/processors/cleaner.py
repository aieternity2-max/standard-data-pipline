import re


class DocumentCleaner:
    """
    Cleans and normalizes document text.
    """

    def clean(self, text: str) -> str:
        """
        Clean document text.

        Operations:
        1. Remove leading/trailing whitespace
        2. Remove indentation from each line
        3. Normalize multiple spaces/tabs
        4. Normalize repeated blank lines
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove leading/trailing whitespace
        # from every line
        text = "\n".join(
            line.strip()
            for line in text.splitlines()
        )

        # Remove excessive spaces/tabs
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Normalize multiple blank lines
        text = re.sub(
            r"\n\s*\n+",
            "\n\n",
            text,
        )

        return text