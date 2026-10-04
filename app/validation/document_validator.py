from dataclasses import dataclass, field

from app.models.document import Document


@dataclass
class ValidationResult:
    """
    Result of validating a Document.
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DocumentValidator:
    """
    Validate standard Document objects.

    Validation checks:
    1. Document ID
    2. Source
    3. Source type
    4. Content
    """

    SUPPORTED_SOURCE_TYPES = {
        "csv",
        "excel",
        "json",
        "jsonl",
        "database",
        "api",
        "txt",
        "pdf",
        "docx",
    }

    def validate(
        self,
        document: Document,
    ) -> ValidationResult:
        """
        Validate a single Document.
        """

        errors: list[str] = []
        warnings: list[str] = []

        # 1. Validate ID
        if not document.id:
            errors.append(
                "Document ID is missing"
            )

        # 2. Validate source
        if not document.source:
            errors.append(
                "Document source is missing"
            )

        # 3. Validate source type
        if not document.source_type:
            errors.append(
                "Document source_type is missing"
            )

        elif (
            document.source_type
            not in self.SUPPORTED_SOURCE_TYPES
        ):
            errors.append(
                f"Unsupported source type: "
                f"{document.source_type}"
            )

        # 4. Validate content
        if document.content is None:
            errors.append(
                "Document content is missing"
            )

        elif not isinstance(
            document.content,
            str,
        ):
            errors.append(
                "Document content must be a string"
            )

        elif not document.content.strip():
            warnings.append(
                "Document content is empty"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_many(
        self,
        documents: list[Document],
    ) -> list[ValidationResult]:
        """
        Validate multiple Documents.
        """

        return [
            self.validate(document)
            for document in documents
        ]