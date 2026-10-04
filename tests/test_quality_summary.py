from app.validation.data_quality import (
    DataQualityResult,
)
from app.validation.quality_summary import (
    QualitySummaryGenerator,
)


def test_quality_summary():

    results = [
        DataQualityResult(
            is_valid=True,
        ),
        DataQualityResult(
            is_valid=True,
        ),
        DataQualityResult(
            is_valid=False,
            errors=["Missing customer_id"],
        ),
        DataQualityResult(
            is_valid=False,
            errors=[
                "Invalid age",
                "Invalid status",
            ],
        ),
    ]

    generator = QualitySummaryGenerator()

    summary = generator.generate(results)

    assert summary.total_records == 4

    assert summary.valid_records == 2

    assert summary.invalid_records == 2

    assert summary.error_count == 3

    assert summary.quality_score == 50.0


def test_quality_summary_warnings():

    results = [
        DataQualityResult(
            is_valid=True,
            warnings=["Empty content"],
        ),
        DataQualityResult(
            is_valid=True,
        ),
    ]

    generator = QualitySummaryGenerator()

    summary = generator.generate(results)

    assert summary.total_records == 2

    assert summary.valid_records == 2

    assert summary.warning_records == 1

    assert summary.warning_count == 1

    assert summary.quality_score == 100.0


def test_empty_quality_summary():

    generator = QualitySummaryGenerator()

    summary = generator.generate([])

    assert summary.total_records == 0

    assert summary.valid_records == 0

    assert summary.invalid_records == 0

    assert summary.quality_score == 100.0