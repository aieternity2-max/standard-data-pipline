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