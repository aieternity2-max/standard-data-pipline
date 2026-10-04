from app.models.document import Document
from app.processors.parser import DocumentParser


def test_document_parser():

    document = Document(
        id="test-1",
        source="sample.txt",
        source_type="txt",
        content="Hello World",
        metadata={},
    )

    parser = DocumentParser()

    result = parser.parse(document)

    assert result == "Hello World"