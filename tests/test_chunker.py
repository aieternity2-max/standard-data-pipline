from app.models.document import Document
from app.processors.chunker import DocumentChunker


def test_document_chunker():

    document = Document(
        id="sample-1",
        source="sample.txt",
        source_type="txt",
        content="abcdefghij",
        metadata={},
    )

    chunker = DocumentChunker(
        chunk_size=5,
        overlap=1,
    )

    chunks = chunker.chunk(document)

    assert len(chunks) == 3

    assert chunks[0].content == "abcde"
    assert chunks[1].content == "efghi"
    assert chunks[2].content == "ij"

    assert chunks[0].metadata["chunk_number"] == 1
    assert chunks[1].metadata["chunk_number"] == 2
    assert chunks[2].metadata["chunk_number"] == 3