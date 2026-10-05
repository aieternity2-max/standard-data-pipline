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

    Supports:
    1. Normal processing using run()
    2. Batch processing using run_batches()
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

        # -----------------------------------------
        # Batch pipeline state
        # -----------------------------------------

        self.last_batch_total_input = 0

        self.last_batch_total_valid = 0

        self.last_batch_total_invalid = 0

        self.last_batch_total_sql = 0

        self.last_batch_total_vector = 0

        self.last_batch_successful = 0

        self.last_batch_failed = 0

    def run(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Validate, process and store documents.

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

        self.logger.info(
            "Quality score: %.2f%%",
            self.last_quality_summary.quality_score,
        )

        # -----------------------------------------
        # 7. Process valid documents
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
        # 8. Store processed documents in state
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
        # 9. SQL Storage
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
        # 10. Vector Storage
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
        # 11. Pipeline completed
        # -----------------------------------------

        self.logger.info(
            "Ingestion pipeline completed"
        )

        # -----------------------------------------
        # 12. Return processed documents
        # -----------------------------------------

        return processed_documents

    def run_batches(
        self,
        batches,
    ) -> list[Document]:
        """
        Process multiple batches of Documents.

        Each batch is processed independently. If a batch
        fails, the error is logged and processing continues
        with the next batch.

        Returns all successfully processed document chunks.
        """

        # -----------------------------------------
        # Batch aggregation state
        # -----------------------------------------

        all_processed_documents = []

        total_sql_records = 0

        total_vector_records = 0

        total_quality_records = 0

        total_valid_records = 0

        total_invalid_records = 0

        successful_batches = 0

        failed_batches = 0

        # -----------------------------------------
        # Process batches
        # -----------------------------------------

        for batch_number, documents in enumerate(
            batches,
            start=1,
        ):

            self.logger.info(
                "Processing batch %d with %d document(s)",
                batch_number,
                len(documents),
            )

            try:

                processed_documents = self.run(
                    documents
                )

                # ---------------------------------
                # Collect processed documents
                # ---------------------------------

                all_processed_documents.extend(
                    processed_documents
                )

                # ---------------------------------
                # Collect storage statistics
                # ---------------------------------

                total_sql_records += (
                    self.last_sql_storage_count
                )

                total_vector_records += (
                    self.last_vector_storage_count
                )

                # ---------------------------------
                # Collect quality statistics
                # ---------------------------------

                if (
                    self.last_quality_summary
                    is not None
                ):

                    total_quality_records += (
                        self.last_quality_summary.total_records
                    )

                    total_valid_records += (
                        self.last_quality_summary.valid_records
                    )

                    total_invalid_records += (
                        self.last_quality_summary.invalid_records
                    )

                successful_batches += 1

                self.logger.info(
                    "Batch %d completed successfully",
                    batch_number,
                )

            except Exception as exc:

                failed_batches += 1

                self.logger.exception(
                    "Batch %d failed: %s",
                    batch_number,
                    exc,
                )

                # Continue with the next batch.
                continue

        # -----------------------------------------
        # Update final pipeline state
        # -----------------------------------------

        self.last_processed_documents = (
            all_processed_documents
        )

        self.last_sql_storage_count = (
            total_sql_records
        )

        self.last_vector_storage_count = (
            total_vector_records
        )

        # -----------------------------------------
        # Store batch statistics
        # -----------------------------------------

        self.last_batch_total_input = (
            total_quality_records
        )

        self.last_batch_total_valid = (
            total_valid_records
        )

        self.last_batch_total_invalid = (
            total_invalid_records
        )

        self.last_batch_total_sql = (
            total_sql_records
        )

        self.last_batch_total_vector = (
            total_vector_records
        )

        self.last_batch_successful = (
            successful_batches
        )

        self.last_batch_failed = (
            failed_batches
        )

        # -----------------------------------------
        # Log batch summary
        # -----------------------------------------

        self.logger.info(
            "Batch ingestion completed"
        )

        self.logger.info(
            "Successful batches: %d",
            successful_batches,
        )

        self.logger.info(
            "Failed batches: %d",
            failed_batches,
        )

        self.logger.info(
            "Total input records: %d",
            total_quality_records,
        )

        self.logger.info(
            "Total valid records: %d",
            total_valid_records,
        )

        self.logger.info(
            "Total invalid records: %d",
            total_invalid_records,
        )

        self.logger.info(
            "Total processed documents: %d",
            len(all_processed_documents),
        )

        self.logger.info(
            "Total SQL records: %d",
            total_sql_records,
        )

        self.logger.info(
            "Total vector records: %d",
            total_vector_records,
        )

        # -----------------------------------------
        # Return successful results
        # -----------------------------------------

        return all_processed_documents