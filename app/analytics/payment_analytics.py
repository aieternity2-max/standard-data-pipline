
"""Payment performance KPIs and revenue-leakage indicators."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader
from app.analytics.validators import TransactionDataValidator


class PaymentAnalytics:
    """Calculate validated payment performance metrics."""

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
        validator: TransactionDataValidator | None = None,
    ) -> None:
        self.data_reader = data_reader or StructuredDataReader()
        self.validator = validator or TransactionDataValidator()

    def analyze(
        self,
        dataframe: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """
        Calculate payment KPIs from a DataFrame.

        If no DataFrame is provided, transaction data is read from MySQL.
        Invalid input raises ValueError rather than producing misleading KPIs.
        """

        if dataframe is None:
            dataframe = self.data_reader.read_transactions()

        validation = self.validator.validate(dataframe)

        if not validation.is_valid:
            raise ValueError(
                "Transaction data validation failed: "
                + "; ".join(validation.errors)
            )

        df = dataframe.copy()

        # Normalize payment statuses without modifying the input DataFrame.
        df["payment_status"] = (
            df["payment_status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        # Convert amounts to numeric values for calculations.
        df["total_amount"] = pd.to_numeric(
            df["total_amount"],
            errors="raise",
        )

        # Convert transaction dates before using Pandas datetime accessors.
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            errors="raise",
        )

        total_transactions = len(df)
        total_value = float(df["total_amount"].sum())

        status_counts = df["payment_status"].value_counts()
        status_values = df.groupby("payment_status")["total_amount"].sum()

        completed_count = int(status_counts.get("completed", 0))
        failed_count = int(status_counts.get("failed", 0))
        pending_count = int(status_counts.get("pending", 0))
        refunded_count = int(status_counts.get("refunded", 0))

        completed_value = float(status_values.get("completed", 0.0))
        failed_value = float(status_values.get("failed", 0.0))
        pending_value = float(status_values.get("pending", 0.0))
        refunded_value = float(status_values.get("refunded", 0.0))

        def percentage(count: int) -> float:
            return round(count / total_transactions * 100, 2)

        # Aggregate transaction counts and values by calendar date.
        df["transaction_day"] = df["transaction_date"].dt.strftime(
            "%Y-%m-%d"
        )

        daily_trends_df = (
            df.groupby("transaction_day", as_index=False)
            .agg(
                transaction_count=("transaction_id", "count"),
                transaction_value=("total_amount", "sum"),
            )
            .rename(columns={"transaction_day": "date"})
        )

        daily_trends_df["transaction_value"] = (
            daily_trends_df["transaction_value"].round(2)
        )

        daily_trends = daily_trends_df.to_dict(orient="records")

        return {
            "total_transactions": total_transactions,
            "total_transaction_value": round(total_value, 2),
            "completed_transactions": completed_count,
            "failed_transactions": failed_count,
            "pending_transactions": pending_count,
            "refunded_transactions": refunded_count,
            "completion_rate_pct": percentage(completed_count),
            "failure_rate_pct": percentage(failed_count),
            "pending_rate_pct": percentage(pending_count),
            "refunded_rate_pct": percentage(refunded_count),
            "completed_transaction_value": round(completed_value, 2),
            "failed_transaction_value": round(failed_value, 2),
            "pending_transaction_value": round(pending_value, 2),
            "refunded_transaction_value": round(refunded_value, 2),
            "potentially_affected_payment_value": round(
                failed_value + pending_value + refunded_value,
                2,
            ),
            "daily_trends": daily_trends,
        }

