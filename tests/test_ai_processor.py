import pytest

from app.ai.ai_processor import AIProcessor
from app.models.document import Document


def test_ai_processor():

    document = Document(
        id="doc-ai-1",
        source="sample.txt",
        source_type="txt",
        content="Hello world from Python",
        metadata={},
    )

    processor = AIProcessor()

    result = processor.process(
        document
    )

    assert result["document_id"] == "doc-ai-1"

    assert (
        result["classification"]
        == "unstructured"
    )

    assert (
        result["extracted"]["content"]
        == "Hello world from Python"
    )

    assert (
        result["extracted"]["word_count"]
        == 4
    )

    assert (
        result["embedding_text"]
        == "Hello world from Python"
    )


def test_ai_processor_mysql():

    document = Document(
        id="mysql-1",
        source="employee",
        source_type="mysql",
        content="John Developer",
        metadata={},
    )

    processor = AIProcessor()

    result = processor.process(
        document
    )

    assert (
        result["classification"]
        == "database"
    )


def test_ai_processor_rejects_invalid_document():

    processor = AIProcessor()

    with pytest.raises(TypeError):

        processor.process(
            "invalid"
        )