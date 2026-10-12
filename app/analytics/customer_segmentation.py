"""Customer value metrics and explainable customer segmentation."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader
from app.analytics.validators import TransactionDataValidator


class CustomerSegmentation:
    """Calculate completed-transaction value and customer segments."""

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
        transaction_validator: TransactionDataValidator | None = None,
        high_value_threshold: float = 200.0,
        regular_value_threshold: float = 50.0,
    ) -> None:
        if high_value_threshold < regular_value_threshold:
            raise ValueError(
                "High-value threshold must be greater than or equal "
                "to the regular-value threshold."
            )

        if regular_value_threshold < 0:
            raise ValueError(
                "Regular-value threshold must not be negative."
            )

        self.data_reader = data_reader or StructuredDataReader()
        self.transaction_validator = (
            transaction_validator or TransactionDataValidator()
        )
        self.high_value_threshold = high_value_threshold
        self.regular_value_threshold = regular_value_threshold

    def analyze(
        self,
        users: pd.DataFrame | None = None,
        transactions: pd.DataFrame | None = None,
        as_of_date: str | pd.Timestamp | None = None,
    ) -> dict[str, Any]:
        """
        Calculate customer value metrics and assign explainable segments.

        Only completed transactions contribute to customer value.
        `as_of_date` can be supplied to make recency calculations
        reproducible in tests and historical analyses.
        """

        if users is None:
            users = self.data_reader.read_users()

        if not isinstance(users, pd.DataFrame):
            raise ValueError("Customer input must be a Pandas DataFrame.")

        if users.empty:
            raise ValueError("Customer dataset is empty.")

        required_user_columns = {"user_id"}
        missing_user_columns = required_user_columns - set(users.columns)

        if missing_user_columns:
            raise ValueError(
                "Missing required customer columns: "
                + ", ".join(sorted(missing_user_columns))
            )

        if users["user_id"].isna().any():
            raise ValueError("Customer IDs must not be missing.")

        if users["user_id"].duplicated().any():
            raise ValueError("Duplicate customer IDs were found.")

        if transactions is None:
            transactions = self.data_reader.read_transactions()

        validation = self.transaction_validator.validate(transactions)

        if not validation.is_valid:
            raise ValueError(
                "Transaction data validation failed: "
                + "; ".join(validation.errors)
            )

        customers = users[["user_id"]].copy()
        payments = transactions.copy()

        payments["payment_status"] = (
            payments["payment_status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        payments["total_amount"] = pd.to_numeric(
            payments["total_amount"],
            errors="raise",
        )

        payments["transaction_date"] = pd.to_datetime(
            payments["transaction_date"],
            errors="raise",
        )

        completed = payments[
            payments["payment_status"] == "completed"
        ].copy()

        completed_summary = (
            completed.groupby("user_id")
            .agg(
                completed_transaction_count=(
                    "transaction_id",
                    "count",
                ),
                total_completed_value=("total_amount", "sum"),
                last_completed_transaction=("transaction_date", "max"),
            )
            .reset_index()
        )

        result = customers.merge(
            completed_summary,
            on="user_id",
            how="left",
            validate="one_to_one",
        )

        result["completed_transaction_count"] = (
            result["completed_transaction_count"]
            .fillna(0)
            .astype(int)
        )

        result["total_completed_value"] = (
            result["total_completed_value"].fillna(0.0).astype(float)
        )

        result["average_completed_transaction_value"] = (
            result["total_completed_value"]
            .div(
                result["completed_transaction_count"].where(
                    result["completed_transaction_count"] > 0
                )
            )
            .fillna(0.0)
        )

        if as_of_date is None:
            reference_date = pd.Timestamp.now().normalize()
        else:
            reference_date = pd.Timestamp(as_of_date).normalize()

        last_dates = pd.to_datetime(
            result["last_completed_transaction"],
            errors="coerce",
        )

        future_dates = last_dates.notna() & (last_dates > reference_date)

        if future_dates.any():
            raise ValueError(
                "Reference date must not precede a completed transaction."
            )

        result["recency_days"] = (
            reference_date - last_dates.dt.normalize()
        ).dt.days.astype("Int64")

        def assign_segment(value: float, count: int) -> str:
            if count == 0:
                return "No Completed Transactions"
            if value >= self.high_value_threshold:
                return "High Value"
            if value >= self.regular_value_threshold:
                return "Regular Value"
            return "Low Value"

        result["customer_segment"] = [
            assign_segment(value, count)
            for value, count in zip(
                result["total_completed_value"],
                result["completed_transaction_count"],
            )
        ]

        result["total_completed_value"] = (
            result["total_completed_value"].round(2)
        )

        result["average_completed_transaction_value"] = (
            result["average_completed_transaction_value"].round(2)
        )

        result["last_completed_transaction"] = (
            result["last_completed_transaction"]
            .dt.strftime("%Y-%m-%d")
        )

        result["last_completed_transaction"] = (
            result["last_completed_transaction"].where(
                result["last_completed_transaction"].notna(),
                None,
            )
        )

        customer_records = result.to_dict(orient="records")

        segment_summary = (
            result.groupby("customer_segment")
            .agg(
                customer_count=("user_id", "nunique"),
                total_completed_value=("total_completed_value", "sum"),
            )
            .reset_index()
            .sort_values("customer_segment")
        )

        segment_summary["total_completed_value"] = (
            segment_summary["total_completed_value"].round(2)
        )

        return {
            "customer_count": len(result),
            "total_completed_transaction_value": round(
                float(completed["total_amount"].sum()),
                2,
            ),
            "high_value_threshold": self.high_value_threshold,
            "regular_value_threshold": self.regular_value_threshold,
            "as_of_date": reference_date.strftime("%Y-%m-%d"),
            "customers": customer_records,
            "segment_summary": segment_summary.to_dict(orient="records"),
        }
