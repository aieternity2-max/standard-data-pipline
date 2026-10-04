from app.models.document import Document

from app.logging.logger import get_logger

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
        self.logger = get_logger(
            "ingestion_pipeline"
        )

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

        # -----------------------------------------
        # 1. Pipeline started
        # -----------------------------------------

        self.logger.info(
            "Ingestion pipeline started"
        )

        self.logger.info(
            "Pipeline received %d document(s)",
            len(documents),
        )

        # -----------------------------------------
        # 2. Validate documents
        # -----------------------------------------

        self.logger.info(
            "Document validation started"
        )

        validation_results = (
            self.document_validator.validate_many(
                documents
            )
        )

        self.logger.info(
            "Document validation completed"
        )

        # -----------------------------------------
        # 3. Separate valid and invalid documents
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
        # 4. Generate quality summary
        # -----------------------------------------

        self.last_quality_summary = (
            self.summary_generator.generate(
                validation_results
            )
        )

        # -----------------------------------------
        # 5. Store invalid documents
        # -----------------------------------------

        self.last_invalid_documents = (
            invalid_documents
        )

        # -----------------------------------------
        # 6. Log quality summary
        # -----------------------------------------

        self.logger.info(
            "Data quality validation completed"
        )

        self.logger.info(
            "Total records: %d",
            self.last_quality_summary.total_records,
        )

        self.logger.info(
            "Valid records: %d",
            self.last_quality_summary.valid_records,
        )

        self.logger.warning(
            "Invalid records: %d",
            self.last_quality_summary.invalid_records,
        )

        self.logger.info(
            "Quality score: %.2f%%",
            self.last_quality_summary.quality_score,
        )

        # -----------------------------------------
        # 7. Pipeline completed
        # -----------------------------------------

        self.logger.info(
            "Ingestion pipeline completed"
        )

        # -----------------------------------------
        # 8. Return valid documents
        # -----------------------------------------

        return valid_documents