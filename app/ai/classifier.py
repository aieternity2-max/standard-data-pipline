class DocumentClassifier:
    """
    Classifies documents based on their source type.

    This is a lightweight deterministic classifier.
    A machine-learning or LLM-based classifier can be
    introduced later without changing the pipeline interface.
    """

    SUPPORTED_TYPES = {
        "csv",
        "excel",
        "json",
        "jsonl",
        "txt",
        "pdf",
        "docx",
        "mysql",
        "database",
        "api",
    }

    def classify(
        self,
        source_type: str,
    ) -> str:
        """
        Classify a document based on its source type.

        Returns
        -------
        str
            Normalized document category.
        """

        if not isinstance(
            source_type,
            str,
        ):
            raise TypeError(
                "source_type must be a string"
            )

        source_type = source_type.strip().lower()

        if not source_type:
            raise ValueError(
                "source_type cannot be empty"
            )

        if source_type not in self.SUPPORTED_TYPES:
            return "unknown"

        if source_type in {
            "csv",
            "excel",
            "json",
            "jsonl",
        }:
            return "structured"

        if source_type in {
            "mysql",
            "database",
        }:
            return "database"

        if source_type == "api":
            return "api"

        return "unstructured"