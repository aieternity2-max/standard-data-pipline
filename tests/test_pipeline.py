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

    result = pipeline.run(documents)

    # -----------------------------------------
    # Pipeline should return processed documents
    # -----------------------------------------

    assert len(result) == 2

    # -----------------------------------------
    # Processed documents should be chunks
    # -----------------------------------------

    assert result[0].id == "customer-1-chunk-1"
    assert result[1].id == "customer-2-chunk-1"

    assert result[0].content == "Alice"
    assert result[1].content == "Bob"

    # -----------------------------------------
    # Chunk metadata should exist
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
    # Quality summary should be generated
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
    # Processed documents should be stored
    # -----------------------------------------

    assert (
        len(
            pipeline.last_processed_documents
        )
        == 2
    )