from app.models.document import Document


class DocumentChunker:
    """
    Splits documents into smaller chunks.

    Chunking is useful for:
    - Large documents
    - Embeddings
    - Vector databases
    - RAG applications
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0"
            )

        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative"
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document: Document,
    ) -> list[Document]:
        """
        Split a Document into smaller Documents.
        """

        if not isinstance(document, Document):
            raise TypeError(
                "document must be an instance of Document"
            )

        content = str(document.content)

        if not content:
            return []

        chunks = []

        start = 0
        chunk_number = 1

        step = (
            self.chunk_size - self.overlap
        )

        while start < len(content):

            end = start + self.chunk_size

            chunk_content = content[
                start:end
            ]

            chunk_metadata = dict(
                document.metadata or {}
            )

            chunk_metadata.update(
                {
                    "chunk_number": chunk_number,
                    "chunk_start": start,
                    "chunk_end": min(
                        end,
                        len(content),
                    ),
                }
            )

            chunk_document = Document(
                id=(
                    f"{document.id}"
                    f"-chunk-{chunk_number}"
                ),
                source=document.source,
                source_type=document.source_type,
                content=chunk_content,
                metadata=chunk_metadata,
            )

            chunks.append(
                chunk_document
            )

            start += step
            chunk_number += 1

        return chunks