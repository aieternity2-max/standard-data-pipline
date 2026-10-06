from app.logging.logger import get_logger

from app.ai.ai_processor import AIProcessor

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
    AI Processing
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
        # AI processing
        # -----------------------------------------

        self.ai_processor = AIProcessor()

        self.last_ai_results = []

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

    # =================================================
    # NORMAL PIPELINE
    # =================================================

    def run(
        self,
        documents,
    ) -> list[Document]:
        """
        Run the ingestion pipeline for a list of documents.

        Flow:

        1. Validate documents
        2. Generate quality summary
        3. AI processing
        4. Parse
        5. Clean
        6. Chunk
        7. Store in SQL
        8. Store in vector database
        """

        # -----------------------------------------
        # Input validation
        # -----------------------------------------

        if not isinstance(
            documents,
            list,
        ):
            raise TypeError(
                "documents must be a list"
            )

        # Reset per-run state
        self.last_invalid_documents = []
        self.last_processed_documents = []
        self.last_ai_results = []
        self.last_sql_storage_count = 0
        self.last_vector_storage_count = 0
        self.last_quality_summary = None

        # -----------------------------------------
        # 1. Validate documents
        # -----------------------------------------

        self.logger.info(
            "Document validation started"
        )

        validation_results = []

        valid_documents = []

        invalid_documents = []

        for document in documents:

            try:

                validation_result = (
                    self.document_validator.validate(
                        document
                    )
                )

                validation_results.append(
                    validation_result
                )

                if validation_result:

                    valid_documents.append(
                        document
                    )

                else:

                    invalid_documents.append(
                        document
                    )

            except Exception as exc:

                self.logger.exception(
                    "Document validation failed: %s",
                    exc,
                )

                invalid_documents.append(
                    document
                )

        # -----------------------------------------
        # Store invalid documents
        # -----------------------------------------

        self.last_invalid_documents = (
            invalid_documents
        )

        self.logger.info(
            "Valid documents: %d",
            len(valid_documents),
        )

        self.logger.info(
            "Invalid documents: %d",
            len(invalid_documents),
        )

        # -----------------------------------------
        # 2. Generate quality summary
        # -----------------------------------------

        self.last_quality_summary = (
            self.summary_generator.generate(
                validation_results
            )
        )

        self.logger.info(
            "Document quality score: %.2f",
            self.last_quality_summary.quality_score,
        )

        # -----------------------------------------
        # 3. AI document processing
        # -----------------------------------------

        self.logger.info(
            "AI document processing started"
        )

        ai_results = []

        for document in valid_documents:

            ai_result = (
                self.ai_processor.process(
                    document
                )
            )

            ai_results.append(
                ai_result
            )

        self.last_ai_results = (
            ai_results
        )

        self.logger.info(
            "AI document processing completed"
        )

        self.logger.info(
            "AI processed documents: %d",
            len(ai_results),
        )

        # -----------------------------------------
        # 4. Process valid documents
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
        # 5. Store processed documents in state
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
        # 6. SQL Storage
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
        # 7. Vector Storage
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
        # 8. Pipeline completed
        # -----------------------------------------

        self.logger.info(
            "Ingestion pipeline completed"
        )

        # -----------------------------------------
        # 9. Return processed documents
        # -----------------------------------------

        return processed_documents

    # =================================================
    # BATCH PIPELINE
    # =================================================

    def run_batches(
        self,
        batches,
    ) -> list[Document]:
        """
        Process multiple batches of Documents.

        Each batch is processed independently.

        If a batch fails:
        - The error is logged.
        - The failed batch is skipped.
        - Processing continues with the next batch.

        Returns all successfully processed
        document chunks.
        """

        # -----------------------------------------
        # Input validation
        # -----------------------------------------

        if batches is None:
            raise ValueError(
                "batches cannot be None"
            )

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

        for batch_number, batch_documents in enumerate(
            batches,
            start=1,
        ):

            self.logger.info(
                "Processing batch %d with %d document(s)",
                batch_number,
                len(batch_documents),
            )

            try:

                # ---------------------------------
                # Run individual batch
                # ---------------------------------

                processed_documents = self.run(
                    batch_documents
                )

                # ---------------------------------
                # Collect processed documents
                # ---------------------------------

                all_processed_documents.extend(
                    processed_documents
                )

                # ---------------------------------
                # Collect SQL statistics
                # ---------------------------------

                total_sql_records += (
                    self.last_sql_storage_count
                )

                # ---------------------------------
                # Collect vector statistics
                # ---------------------------------

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

                # ---------------------------------
                # Mark batch successful
                # ---------------------------------

                successful_batches += 1

                self.logger.info(
                    "Batch %d completed successfully",
                    batch_number,
                )

            except Exception as exc:

                # ---------------------------------
                # Mark batch failed
                # ---------------------------------

                failed_batches += 1

                self.logger.exception(
                    "Batch %d failed: %s",
                    batch_number,
                    exc,
                )

                # ---------------------------------
                # Continue with next batch
                # ---------------------------------

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