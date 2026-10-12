
"""DataFrame validation for structured transaction analytics."""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class AnalyticsValidationResult:
    """Result of validating structured transaction data."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class TransactionDataValidator:
    """Validate transaction data before KPI calculations."""

    REQUIRED_COLUMNS = {
        "transaction_id",
        "user_id",
        "total_amount",
        "payment_status",
        "transaction_date",
    }

    ALLOWED_STATUSES = {
        "completed",
        "failed",
        "pending",
    }

    def validate(
        self,
        dataframe: pd.DataFrame,
    ) -> AnalyticsValidationResult:
        """Validate a transaction DataFrame."""

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(dataframe, pd.DataFrame):
            return AnalyticsValidationResult(
                is_valid=False,
                errors=["Input must be a Pandas DataFrame."],
            )

        if dataframe.empty:
            return AnalyticsValidationResult(
                is_valid=False,
                errors=["Transaction dataset is empty."],
            )

        missing_columns = self.REQUIRED_COLUMNS - set(dataframe.columns)

        if missing_columns:
            errors.append(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

            return AnalyticsValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
            )

        # Transaction IDs must be present and unique.
        if dataframe["transaction_id"].isna().any():
            errors.append("Transaction IDs must not be missing.")

        if dataframe["transaction_id"].duplicated().any():
            errors.append("Duplicate transaction IDs were found.")

        # Customer identifiers must be present.
        if dataframe["user_id"].isna().any():
            errors.append("User IDs must not be missing.")

        # Amounts must be numeric, present, and non-negative.
        numeric_amounts = pd.to_numeric(
            dataframe["total_amount"],
            errors="coerce",
        )

        if numeric_amounts.isna().any():
            errors.append(
                "Transaction amounts must be present and numeric."
            )
        elif (numeric_amounts < 0).any():
            errors.append(
                "Transaction amounts must not be negative."
            )

        # Payment statuses must be recognized.
        statuses = dataframe["payment_status"]

        if statuses.isna().any():
            errors.append("Payment statuses must not be missing.")

        normalized_statuses = (
            statuses.astype("string")
            .str.strip()
            .str.lower()
        )

        if normalized_statuses.eq("").any():
            errors.append("Payment statuses must not be empty.")

        unknown_statuses = (
            set(normalized_statuses.dropna().unique())
            - self.ALLOWED_STATUSES
            - {""}
        )

        if unknown_statuses:
            errors.append(
                "Unsupported payment statuses: "
                + ", ".join(sorted(unknown_statuses))
            )

        # Transaction dates must be present and valid.
        try:
            dates = pd.to_datetime(
                dataframe["transaction_date"],
                errors="coerce",
                format="mixed",
            )

            if dates.isna().any():
                errors.append(
                    "Transaction dates must be present and valid."
                )

        except (TypeError, ValueError, OverflowError):
            errors.append(
                "Transaction dates must be present and valid."
            )

        return AnalyticsValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )
