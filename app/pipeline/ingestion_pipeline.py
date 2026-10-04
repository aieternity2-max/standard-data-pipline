from app.models.document import Document

from app.validation.document_validator import (
    DocumentValidator,
)

from app.validation.quality_summary import (
    QualitySummaryGenerator,
)


class IngestionPipeline:
    """
    Main processing pipeline.

    Flow:

    Documents
        ↓
    Document Validation
        ↓
    Quality Summary
        ↓
    Valid Documents
    """

    def __init__(self):
        self.document_validator = (
            DocumentValidator()
        )

        self.summary_generator = (
            QualitySummaryGenerator()
        )

        self.last_quality_summary = None
        self.last_invalid_documents = []

    def run(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Validate and process ingested documents.

        Returns only valid documents.
        """

        print(
            f"Pipeline received {len(documents)} document(s)"
        )

        # -----------------------------------------
        # 1. Validate documents
        # -----------------------------------------

        validation_results = (
            self.document_validator.validate_many(
                documents
            )
        )

        # -----------------------------------------
        # 2. Separate valid and invalid documents
        # -----------------------------------------

        valid_documents = []
        invalid_documents = []

        for document, result in zip(
            documents,
            validation_results,
        ):

            if result.is_valid:

                valid_documents.append(
                    document
                )

            else:

                invalid_documents.append(
                    document
                )

        # -----------------------------------------
        # 3. Generate quality summary
        # -----------------------------------------

        self.last_quality_summary = (
            self.summary_generator.generate(
                validation_results
            )
        )

        # -----------------------------------------
        # 4. Store invalid documents
        # -----------------------------------------

        self.last_invalid_documents = (
            invalid_documents
        )

        # -----------------------------------------
        # 5. Print quality information
        # -----------------------------------------

        print(
            "Data Quality Summary"
        )

        print(
            f"Total Records: "
            f"{self.last_quality_summary.total_records}"
        )

        print(
            f"Valid Records: "
            f"{self.last_quality_summary.valid_records}"
        )

        print(
            f"Invalid Records: "
            f"{self.last_quality_summary.invalid_records}"
        )

        print(
            f"Quality Score: "
            f"{self.last_quality_summary.quality_score}%"
        )

        # -----------------------------------------
        # 6. Return valid documents
        # -----------------------------------------

        return valid_documents