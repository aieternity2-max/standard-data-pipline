from app.models.document import Document
from app.validation.document_validator import (
    DocumentValidator,
)


def test_valid_document():

    document = Document(
        id="sample-1",
        source="sample.csv",
        source_type="csv",
        content="customer_id: 101",
        metadata={
            "row_number": 1,
        },
    )

    validator = DocumentValidator()

    result = validator.validate(document)

    assert result.is_valid is True

    assert result.errors == []

    assert result.warnings == []


def test_missing_content():

    document = Document(
        id="sample-1",
        source="sample.csv",
        source_type="csv",
        content="",
        metadata={},
    )

    validator = DocumentValidator()

    result = validator.validate(document)

    assert result.is_valid is True

    assert "Document content is empty" in (
        result.warnings
    )


def test_unsupported_source_type():

    document = Document(
        id="sample-1",
        source="sample.xyz",
        source_type="unknown",
        content="some data",
        metadata={},
    )

    validator = DocumentValidator()

    result = validator.validate(document)

    assert result.is_valid is False

    assert (
        "Unsupported source type: unknown"
        in result.errors
    )


def test_missing_source():

    document = Document(
        id="sample-1",
        source="",
        source_type="csv",
        content="some data",
        metadata={},
    )

    validator = DocumentValidator()

    result = validator.validate(document)

    assert result.is_valid is False

    assert (
        "Document source is missing"
        in result.errors
    )


def test_validate_many():

    documents = [
        Document(
            id="sample-1",
            source="sample.csv",
            source_type="csv",
            content="Alice",
            metadata={},
        ),
        Document(
            id="sample-2",
            source="sample.csv",
            source_type="csv",
            content="Bob",
            metadata={},
        ),
    ]

    validator = DocumentValidator()

    results = validator.validate_many(
        documents
    )

    assert len(results) == 2

    assert all(
        result.is_valid
        for result in results
    )