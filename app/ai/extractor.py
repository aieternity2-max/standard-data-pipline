from app.models.document import Document


class DocumentExtractor:
    """
    Extracts basic information from a Document.

    This provides a deterministic extraction layer that can
    later be extended with NLP or LLM-based extraction.
    """

    def extract(
        self,
        document: Document,
    ) -> dict:
        """
        Extract useful information from a document.

        Returns
        -------
        dict
            Extracted document information.
        """

        if not isinstance(
            document,
            Document,
        ):
            raise TypeError(
                "document must be a Document instance"
            )

        content = document.content.strip()

        if not content:
            raise ValueError(
                "document content cannot be empty"
            )

        return {
            "document_id": document.id,
            "source": document.source,
            "source_type": document.source_type,
            "content": content,
            "content_length": len(content),
            "word_count": len(
                content.split()
            ),
        }