"""Revenue and payment performance analytics."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader
from app.analytics.validators import TransactionDataValidator


class RevenueAnalytics:
    """Analyze transaction values, payment statuses, and revenue trends."""

    REQUIRED_COLUMNS = {
        "transaction_id",
        "user_id",
        "total_amount",
        "payment_status",
        "transaction_date",
    }

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
    ) -> None:
        self.data_reader = data_reader or StructuredDataReader()
        self.validator = TransactionDataValidator()

    def analyze(
        self,
        dataframe: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """Validate transactions and calculate revenue-related metrics."""

        if dataframe is None:
            dataframe = self.data_reader.read_transactions()

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError(
                "Transaction input must be a Pandas DataFrame."
            )

        missing_columns = self.REQUIRED_COLUMNS.difference(
            dataframe.columns
        )

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Missing required transaction columns: {missing}"
            )

        transactions = dataframe.copy(deep=True)

        if transactions.empty:
            return self._empty_result()

        validation_result = self.validator.validate(transactions)

        if not validation_result.is_valid:
            details = "; ".join(validation_result.errors)
            raise ValueError(
                f"Transaction data validation failed: {details}"
            )

        # Use a separate working copy for numeric and date operations.
        transactions["total_amount"] = pd.to_numeric(
            transactions["total_amount"],
            errors="raise",
        )
        transactions["transaction_date"] = pd.to_datetime(
            transactions["transaction_date"],
            errors="raise",
        )
        transactions["payment_status"] = (
            transactions["payment_status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        total_transactions = len(transactions)
        total_transaction_value = round(
            float(transactions["total_amount"].sum()), 2
        )

        status_breakdown = []
        for status in sorted(transactions["payment_status"].unique()):
            status_transactions = transactions[
                transactions["payment_status"] == status
            ]

            status_breakdown.append(
                {
                    "payment_status": str(status),
                    "transaction_count": int(len(status_transactions)),
                    "transaction_value": round(
                        float(status_transactions["total_amount"].sum()),
                        2,
                    ),
                }
            )

        completed = transactions[
            transactions["payment_status"] == "completed"
        ]
        failed = transactions[
            transactions["payment_status"] == "failed"
        ]
        pending = transactions[
            transactions["payment_status"] == "pending"
        ]
        refunded = transactions[
            transactions["payment_status"] == "refunded"
        ]

        revenue_trend = (
            completed.assign(
                period=completed["transaction_date"].dt.strftime("%Y-%m")
            )
            .groupby("period")
            .agg(
                completed_transaction_count=("transaction_id", "count"),
                completed_transaction_value=("total_amount", "sum"),
            )
            .sort_index()
            .reset_index()
        )

        trend_records = [
            {
                "period": str(row["period"]),
                "completed_transaction_count": int(
                    row["completed_transaction_count"]
                ),
                "completed_transaction_value": round(
                    float(row["completed_transaction_value"]), 2
                ),
            }
            for _, row in revenue_trend.iterrows()
        ]

        return {
            "total_transactions": int(total_transactions),
            "total_transaction_value": total_transaction_value,
            "completed_transaction_count": int(len(completed)),
            "completed_transaction_value": round(
                float(completed["total_amount"].sum()), 2
            ),
            "failed_transaction_count": int(len(failed)),
            "failed_transaction_value": round(
                float(failed["total_amount"].sum()), 2
            ),
            "pending_transaction_count": int(len(pending)),
            "pending_transaction_value": round(
                float(pending["total_amount"].sum()), 2
            ),
            "refunded_transaction_count": int(len(refunded)),
            "refunded_transaction_value": round(
                float(refunded["total_amount"].sum()), 2
            ),
            "payment_status_breakdown": status_breakdown,
            "revenue_trend": trend_records,
        }

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        """Return consistent zero metrics for an empty transaction table."""
        return {
            "total_transactions": 0,
            "total_transaction_value": 0.00,
            "completed_transaction_count": 0,
            "completed_transaction_value": 0.00,
            "failed_transaction_count": 0,
            "failed_transaction_value": 0.00,
            "pending_transaction_count": 0,
            "pending_transaction_value": 0.00,
            "refunded_transaction_count": 0,
            "refunded_transaction_value": 0.00,
            "payment_status_breakdown": [],
            "revenue_trend": [],
        }
