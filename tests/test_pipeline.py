from app.config.settings import settings
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.models.document import Document


def test_application_configuration():

    assert settings.app_name == "Standard Data Pipeline"

    assert settings.environment == "development"


def test_ingestion_pipeline_validation_and_processing():

    documents = [
        Document(
            id="customer-1",
            source="sample.csv",
            source_type="csv",
            content="Alice",
            metadata={},
        ),
        Document(
            id="customer-2",
            source="sample.csv",
            source_type="csv",
            content="Bob",
            metadata={},
        ),
    ]

    pipeline = IngestionPipeline()

    # -----------------------------------------
    # Mock storage components
    # -----------------------------------------

    sql_saved = []

    vector_saved = []

    def mock_sql_save(documents):
        sql_saved.extend(documents)
        return len(documents)

    def mock_vector_save(documents):
        vector_saved.extend(documents)
        return len(documents)

    pipeline.sql_storage.save = mock_sql_save

    pipeline.vector_storage.save = mock_vector_save

    # -----------------------------------------
    # Run pipeline
    # -----------------------------------------

    result = pipeline.run(documents)

    # -----------------------------------------
    # Processed documents
    # -----------------------------------------

    assert len(result) == 2

    assert result[0].id == "customer-1-chunk-1"
    assert result[1].id == "customer-2-chunk-1"

    assert result[0].content == "Alice"
    assert result[1].content == "Bob"

    # -----------------------------------------
    # Chunk metadata
    # -----------------------------------------

    assert (
        result[0].metadata["chunk_number"]
        == 1
    )

    assert (
        result[1].metadata["chunk_number"]
        == 1
    )

    # -----------------------------------------
    # Quality summary
    # -----------------------------------------

    assert (
        pipeline.last_quality_summary
        is not None
    )

    assert (
        pipeline.last_quality_summary.total_records
        == 2
    )

    assert (
        pipeline.last_quality_summary.valid_records
        == 2
    )

    assert (
        pipeline.last_quality_summary.invalid_records
        == 0
    )

    assert (
        pipeline.last_quality_summary.quality_score
        == 100.0
    )

    # -----------------------------------------
    # No invalid documents
    # -----------------------------------------

    assert len(
        pipeline.last_invalid_documents
    ) == 0

    # -----------------------------------------
    # Processed documents stored in pipeline
    # -----------------------------------------

    assert (
        len(
            pipeline.last_processed_documents
        )
        == 2
    )

    # -----------------------------------------
    # SQL storage verification
    # -----------------------------------------

    assert (
        pipeline.last_sql_storage_count
        == 2
    )

    assert len(sql_saved) == 2

    assert (
        sql_saved[0].id
        == "customer-1-chunk-1"
    )

    assert (
        sql_saved[1].id
        == "customer-2-chunk-1"
    )

    # -----------------------------------------
    # Vector storage verification
    # -----------------------------------------

    assert (
        pipeline.last_vector_storage_count
        == 2
    )

    assert len(vector_saved) == 2

    assert (
        vector_saved[0].id
        == "customer-1-chunk-1"
    )

    assert (
        vector_saved[1].id
        == "customer-2-chunk-1"
    )

def test_ingestion_pipeline_batches():

    batches = [
        [
            Document(
                id="batch-1-doc-1",
                source="sample.csv",
                source_type="csv",
                content="Alice",
                metadata={},
            ),
            Document(
                id="batch-1-doc-2",
                source="sample.csv",
                source_type="csv",
                content="Bob",
                metadata={},
            ),
        ],
        [
            Document(
                id="batch-2-doc-1",
                source="sample.csv",
                source_type="csv",
                content="Charlie",
                metadata={},
            ),
        ],
    ]

    pipeline = IngestionPipeline()

    # -----------------------------------------
    # Mock storage components
    # -----------------------------------------

    sql_saved = []

    vector_saved = []

    def mock_sql_save(documents):
        sql_saved.extend(documents)
        return len(documents)

    def mock_vector_save(documents):
        vector_saved.extend(documents)
        return len(documents)

    pipeline.sql_storage.save = mock_sql_save

    pipeline.vector_storage.save = mock_vector_save

    # -----------------------------------------
    # Run batches
    # -----------------------------------------

    result = pipeline.run_batches(
        batches
    )

    # -----------------------------------------
    # Verify processed documents
    # -----------------------------------------

    assert len(result) == 3

    assert result[0].id == "batch-1-doc-1-chunk-1"
    assert result[1].id == "batch-1-doc-2-chunk-1"
    assert result[2].id == "batch-2-doc-1-chunk-1"

    # -----------------------------------------
    # Verify SQL storage
    # -----------------------------------------

    assert len(sql_saved) == 3

    assert (
        pipeline.last_sql_storage_count
        == 3
    )

    # -----------------------------------------
    # Verify vector storage
    # -----------------------------------------

    assert len(vector_saved) == 3

    assert (
        pipeline.last_vector_storage_count
        == 3
    )

    # -----------------------------------------
    # Verify final pipeline state
    # -----------------------------------------

    assert (
        len(
            pipeline.last_processed_documents
        )
        == 3
    )
def test_ingestion_pipeline_continues_after_batch_failure():

    batches = [
        [
            Document(
                id="batch-1-doc-1",
                source="sample.csv",
                source_type="csv",
                content="Alice",
                metadata={},
            ),
        ],
        [
            Document(
                id="batch-2-doc-1",
                source="sample.csv",
                source_type="csv",
                content="Bob",
                metadata={},
            ),
        ],
        [
            Document(
                id="batch-3-doc-1",
                source="sample.csv",
                source_type="csv",
                content="Charlie",
                metadata={},
            ),
        ],
    ]

    pipeline = IngestionPipeline()

    original_run = pipeline.run

    call_count = 0

    def mock_run(documents):

        nonlocal call_count

        call_count += 1

        if call_count == 2:
            raise RuntimeError(
                "Simulated batch failure"
            )

        return original_run(documents)

    pipeline.run = mock_run

    result = pipeline.run_batches(batches)

    # -----------------------------------------
    # Batch 1 and Batch 3 should succeed
    # Batch 2 should fail
    # -----------------------------------------

    assert len(result) == 2

    assert result[0].id == (
        "batch-1-doc-1-chunk-1"
    )

    assert result[1].id == (
        "batch-3-doc-1-chunk-1"
    )
def test_ingestion_pipeline_ai_can_be_disabled():

    from app.config.settings import Settings

    documents = [
        Document(
            id="ai-disabled-1",
            source="sample.txt",
            source_type="txt",
            content="Hello world",
            metadata={},
        ),
    ]

    pipeline = IngestionPipeline()

    # Disable AI processing
    pipeline.settings = Settings(
        ai_enabled=False
    )

    # Mock storage
    pipeline.sql_storage.save = (
        lambda documents: len(documents)
    )

    pipeline.vector_storage.save = (
        lambda documents: len(documents)
    )

    result = pipeline.run(documents)

    assert len(result) == 1
    assert result[0].id == "ai-disabled-1-chunk-1"