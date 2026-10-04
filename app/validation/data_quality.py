from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataQualityResult:
    """
    Result of a data-quality validation.
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DataQualityValidator:
    """
    Validate structured records against
    configurable data-quality rules.
    """

    def __init__(
        self,
        required_fields: list[str] | None = None,
        field_types: dict[str, type] | None = None,
        allowed_values: dict[str, set[Any]] | None = None,
    ):
        self.required_fields = (
            required_fields or []
        )

        self.field_types = (
            field_types or {}
        )

        self.allowed_values = (
            allowed_values or {}
        )

    def validate_record(
        self,
        record: dict[str, Any],
    ) -> DataQualityResult:
        """
        Validate one record.
        """

        errors: list[str] = []
        warnings: list[str] = []

        # -------------------------------------------------
        # 1. Required field validation
        # -------------------------------------------------

        for field in self.required_fields:

            if field not in record:

                errors.append(
                    f"Required field missing: {field}"
                )

            elif (
                record[field] is None
                or record[field] == ""
            ):

                errors.append(
                    f"Required field is empty: {field}"
                )

        # -------------------------------------------------
        # 2. Data type validation
        # -------------------------------------------------

        for field, expected_type in (
            self.field_types.items()
        ):

            if field not in record:
                continue

            value = record[field]

            if value is None:
                continue

            if not isinstance(
                value,
                expected_type,
            ):

                errors.append(
                    f"Invalid type for {field}: "
                    f"expected "
                    f"{expected_type.__name__}, "
                    f"got "
                    f"{type(value).__name__}"
                )

        # -------------------------------------------------
        # 3. Allowed-value validation
        # -------------------------------------------------

        for field, allowed in (
            self.allowed_values.items()
        ):

            if field not in record:
                continue

            value = record[field]

            if value is None:
                continue

            if value not in allowed:

                errors.append(
                    f"Invalid value for {field}: "
                    f"{value}"
                )

        # -------------------------------------------------
        # 4. Empty record warning
        # -------------------------------------------------

        if not record:

            warnings.append(
                "Record is empty"
            )

        return DataQualityResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_records(
        self,
        records: list[dict[str, Any]],
    ) -> list[DataQualityResult]:
        """
        Validate multiple records.
        """

        return [
            self.validate_record(record)
            for record in records
        ]

    def find_duplicates(
        self,
        records: list[dict[str, Any]],
        key_fields: list[str],
    ) -> list[dict[str, Any]]:
        """
        Find duplicate records based on key fields.

        Example:

        key_fields = ["customer_id"]
        """

        seen: set[tuple[Any, ...]] = set()

        duplicates: list[dict[str, Any]] = []

        for record in records:

            key = tuple(
                record.get(field)
                for field in key_fields
            )

            if key in seen:
                duplicates.append(record)
            else:
                seen.add(key)

        return duplicates