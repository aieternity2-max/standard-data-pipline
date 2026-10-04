from dataclasses import dataclass

from app.validation.data_quality import DataQualityResult


@dataclass
class QualitySummary:
    """
    Summary of data-quality validation results.
    """

    total_records: int
    valid_records: int
    invalid_records: int
    warning_records: int
    error_count: int
    warning_count: int
    quality_score: float

    @property
    def duplicate_count(self) -> int:
        """
        Reserved for duplicate detection statistics.
        """
        return 0


class QualitySummaryGenerator:
    """
    Generate a summary from validation results.
    """

    def generate(
        self,
        results: list[DataQualityResult],
    ) -> QualitySummary:

        total_records = len(results)

        valid_records = sum(
            result.is_valid
            for result in results
        )

        invalid_records = (
            total_records - valid_records
        )

        warning_records = sum(
            bool(result.warnings)
            for result in results
        )

        error_count = sum(
            len(result.errors)
            for result in results
        )

        warning_count = sum(
            len(result.warnings)
            for result in results
        )

        if total_records == 0:
            quality_score = 100.0
        else:
            quality_score = round(
                (
                    valid_records
                    / total_records
                )
                * 100,
                2,
            )

        return QualitySummary(
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            warning_records=warning_records,
            error_count=error_count,
            warning_count=warning_count,
            quality_score=quality_score,
        )