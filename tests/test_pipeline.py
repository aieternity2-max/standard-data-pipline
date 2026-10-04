from app.config.settings import settings
from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.models.document import Document



def test_application_configuration():

    assert settings.app_name == "Standard Data Pipeline"

    assert settings.environment == "development"


def test_ingestion_pipeline_validation():

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

    # Pipeline should return valid documents
    assert len(result) == 2

    # Quality summary should be generated
    assert pipeline.last_quality_summary is not None

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

    # No invalid documents
    assert len(
        pipeline.last_invalid_documents
    ) == 0