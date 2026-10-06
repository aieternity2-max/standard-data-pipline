import pytest

from app.ai.extractor import DocumentExtractor
from app.models.document import Document


def test_document_extractor():

    document = Document(
        id="doc-1",
        source="sample.txt",
        source_type="txt",
        content="Hello world from Python",
        metadata={},
    )

    extractor = DocumentExtractor()

    result = extractor.extract(document)

    assert result["document_id"] == "doc-1"
    assert result["source"] == "sample.txt"
    assert result["source_type"] == "txt"
    assert result["content"] == "Hello world from Python"
    assert result["content_length"] == 23
    assert result["word_count"] == 4


def test_document_extractor_strips_content():

    document = Document(
        id="doc-2",
        source="sample.txt",
        source_type="txt",
        content="   Hello world   ",
        metadata={},
    )

    extractor = DocumentExtractor()

    result = extractor.extract(document)

    assert result["content"] == "Hello world"


def test_document_extractor_rejects_invalid_document():

    extractor = DocumentExtractor()

    with pytest.raises(TypeError):
        extractor.extract("not a document")


def test_document_extractor_rejects_empty_content():

    document = Document(
        id="doc-3",
        source="sample.txt",
        source_type="txt",
        content="   ",
        metadata={},
    )

    extractor = DocumentExtractor()

    with pytest.raises(ValueError):
        extractor.extract(document)