from app.models.document import Document


class DocumentParser:
    """
    Parses standardized Documents into a consistent
    text representation.

    The parser does not modify the original Document.
    """

    def parse(self, document: Document) -> str:
        """
        Extract textual content from a Document.
        """

        if not isinstance(document, Document):
            raise TypeError(
                "document must be an instance of Document"
            )

        if document.content is None:
            return ""

        return str(document.content)