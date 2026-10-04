from app.logging.logger import get_logger

from app.processors.parser import DocumentParser
from app.processors.cleaner import DocumentCleaner
from app.processors.chunker import DocumentChunker

from app.storage.sql_storage import SQLStorage
from app.storage.vector_storage import VectorStorage

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
    Valid Documents
        ↓
    Parser
        ↓
    Cleaner
        ↓
    Chunker
        ↓
    Processed Documents
        ↓
    SQL Storage
        ↓
    Vector Storage
    """

    def __init__(self):

        # -----------------------------------------
        # Logger
        # -----------------------------------------

        self.logger = get_logger(
            "ingestion_pipeline"
        )

        # -----------------------------------------
        # Validation components
        # -----------------------------------------

        self.document_validator = (
            DocumentValidator()
        )

        self.summary_generator = (
            QualitySummaryGenerator()
        )

        # -----------------------------------------
        # Processing components
        # -----------------------------------------

        self.parser = DocumentParser()

        self.cleaner = DocumentCleaner()

        self.chunker = DocumentChunker()

        # -----------------------------------------
        # Storage components
        # -----------------------------------------

        self.sql_storage = SQLStorage()

        self.vector_storage = VectorStorage()

        # -----------------------------------------
        # Pipeline state
        # -----------------------------------------

        self.last_quality_summary = None

        self.last_invalid_documents = []

        self.last_processed_documents = []

        self.last_sql_storage_count = 0

        self.last_vector_storage_count = 0

    def run(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Validate, process and prepare documents
        for storage.

        Returns processed document chunks.
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

        # -----------------------------------------
        # 7. Log invalid records
        # -----------------------------------------

        invalid_count = (
            self.last_quality_summary.invalid_records
        )

        if invalid_count > 0:

            self.logger.warning(
                "Invalid records: %d",
                invalid_count,
            )

        else:

            self.logger.info(
                "Invalid records: %d",
                invalid_count,
            )

        # -----------------------------------------
        # 8. Log quality score
        # -----------------------------------------

        self.logger.info(
            "Quality score: %.2f%%",
            self.last_quality_summary.quality_score,
        )

        # -----------------------------------------
        # 9. Process valid documents
        # -----------------------------------------

        self.logger.info(
            "Document processing started"
        )

        processed_documents = []

        for document in valid_documents:

            # -------------------------------------
            # Parse
            # -------------------------------------

            parsed_content = (
                self.parser.parse(
                    document
                )
            )

            # -------------------------------------
            # Clean
            # -------------------------------------

            cleaned_content = (
                self.cleaner.clean(
                    parsed_content
                )
            )

            # -------------------------------------
            # Create cleaned document
            # -------------------------------------

            cleaned_document = Document(
                id=document.id,
                source=document.source,
                source_type=document.source_type,
                content=cleaned_content,
                metadata=dict(
                    document.metadata or {}
                ),
            )

            # -------------------------------------
            # Chunk
            # -------------------------------------

            chunks = self.chunker.chunk(
                cleaned_document
            )

            processed_documents.extend(
                chunks
            )

        # -----------------------------------------
        # 10. Store processed documents
        # -----------------------------------------

        self.last_processed_documents = (
            processed_documents
        )

        self.logger.info(
            "Document processing completed"
        )

        self.logger.info(
            "Processed documents: %d",
            len(processed_documents),
        )

        # -----------------------------------------
        # 11. SQL Storage
        # -----------------------------------------

        self.logger.info(
            "SQL storage processing started"
        )

        self.last_sql_storage_count = (
            self.sql_storage.save(
                processed_documents
            )
        )

        self.logger.info(
            "SQL storage processed %d document(s)",
            self.last_sql_storage_count,
        )

        # -----------------------------------------
        # 12. Vector Storage
        # -----------------------------------------

        self.logger.info(
            "Vector storage processing started"
        )

        self.last_vector_storage_count = (
            self.vector_storage.save(
                processed_documents
            )
        )

        self.logger.info(
            "Vector storage processed %d document(s)",
            self.last_vector_storage_count,
        )

        # -----------------------------------------
        # 13. Pipeline completed
        # -----------------------------------------

        self.logger.info(
            "Ingestion pipeline completed"
        )

        # -----------------------------------------
        # 14. Return processed documents
        # -----------------------------------------

        return processed_documents