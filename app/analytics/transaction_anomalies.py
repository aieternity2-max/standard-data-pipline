"""Explainable rule-based transaction anomaly detection."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader
from app.analytics.validators import TransactionDataValidator


class TransactionAnomalyDetector:
    """Flag transactions that warrant further investigation."""

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
        validator: TransactionDataValidator | None = None,
        high_value_threshold: float = 500.0,
        repeat_window_minutes: int = 5,
        repeat_minimum_count: int = 2,
        failed_minimum_count: int = 2,
        unsuccessful_minimum_count: int = 2,
    ) -> None:
        if high_value_threshold <= 0:
            raise ValueError("The high-value threshold must be positive.")

        if repeat_window_minutes <= 0:
            raise ValueError("The repeat window must be positive.")

        if repeat_minimum_count < 2:
            raise ValueError("The repeat minimum count must be at least 2.")

        if failed_minimum_count < 2:
            raise ValueError("The failed minimum count must be at least 2.")

        if unsuccessful_minimum_count < 2:
            raise ValueError(
                "The unsuccessful minimum count must be at least 2."
            )

        self.data_reader = data_reader or StructuredDataReader()
        self.validator = validator or TransactionDataValidator()
        self.high_value_threshold = float(high_value_threshold)
        self.repeat_window_minutes = repeat_window_minutes
        self.repeat_minimum_count = repeat_minimum_count
        self.failed_minimum_count = failed_minimum_count
        self.unsuccessful_minimum_count = unsuccessful_minimum_count

    def analyze(
        self,
        dataframe: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """Detect rule-based anomalies in validated transaction data."""

        if dataframe is None:
            dataframe = self.data_reader.read_transactions()

        validation = self.validator.validate(dataframe)

        if not validation.is_valid:
            raise ValueError(
                "Transaction data validation failed: "
                + "; ".join(validation.errors)
            )

        df = dataframe.copy()

        df["payment_status"] = (
            df["payment_status"]
            .astype("string")
            .str.strip()
            .str.lower()
        )
        df["total_amount"] = pd.to_numeric(
            df["total_amount"],
            errors="raise",
        )
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            errors="raise",
            format="mixed",
        )

        anomalies: list[dict[str, Any]] = []

        def flag(
            row: pd.Series,
            rule: str,
            reason: str,
        ) -> None:
            anomalies.append(
                {
                    "transaction_id": row["transaction_id"],
                    "user_id": row["user_id"],
                    "total_amount": round(float(row["total_amount"]), 2),
                    "payment_status": str(row["payment_status"]),
                    "transaction_date": row["transaction_date"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "rule": rule,
                    "reason": reason,
                }
            )

        # Rule 1: flag amounts at or above the configured threshold.
        high_value = df[
            df["total_amount"] >= self.high_value_threshold
        ]

        for _, row in high_value.iterrows():
            flag(
                row,
                "high_value_transaction",
                (
                    f"Transaction amount is at least "
                    f"{self.high_value_threshold:.2f}."
                ),
            )

        # Rule 2: flag every transaction in a same-customer cluster
        # containing the minimum number of attempts within the time window.
        ordered = df.sort_values(
            ["user_id", "transaction_date", "transaction_id"]
        )

        rapid_ids: set[Any] = set()

        for _, customer_rows in ordered.groupby("user_id", sort=False):
            customer_rows = customer_rows.sort_values("transaction_date")
            records = list(customer_rows.iterrows())

            for start in range(len(records)):
                window_start = records[start][1]["transaction_date"]
                window_end = (
                    window_start
                    + pd.Timedelta(self.repeat_window_minutes, unit="min")
                )

                matching = [
                    record
                    for record in records[start:]
                    if record[1]["transaction_date"] <= window_end
                ]

                if len(matching) >= self.repeat_minimum_count:
                    rapid_ids.update(
                        record[1]["transaction_id"]
                        for record in matching
                    )

        for _, row in df[df["transaction_id"].isin(rapid_ids)].iterrows():
            flag(
                row,
                "rapid_repeated_transactions",
                (
                    f"Customer has at least {self.repeat_minimum_count} "
                    f"transactions within {self.repeat_window_minutes} "
                    "minutes."
                ),
            )

        # Rule 3: flag failed transactions for customers with repeated failures.
        failed = df[df["payment_status"] == "failed"]
        failed_counts = failed.groupby("user_id").size()
        repeated_failed_users = set(
            failed_counts[
                failed_counts >= self.failed_minimum_count
            ].index
        )

        repeated_failed = failed[
            failed["user_id"].isin(repeated_failed_users)
        ]

        for _, row in repeated_failed.iterrows():
            flag(
                row,
                "repeated_failed_transactions",
                (
                    f"Customer has at least {self.failed_minimum_count} "
                    "failed transactions in the supplied dataset."
                ),
            )

               # Rule 4: flag customers with both failed and pending transactions.
        unsuccessful = df[
            df["payment_status"].isin(["failed", "pending"])
        ]

        unsuccessful_counts = unsuccessful.groupby("user_id").size()

        unsuccessful_status_counts = (
            unsuccessful.pivot_table(
                index="user_id",
                columns="payment_status",
                values="transaction_id",
                aggfunc="count",
                fill_value=0,
            )
        )

        failed_counts = unsuccessful_status_counts.get(
            "failed",
            pd.Series(dtype="int64"),
        )
        pending_counts = unsuccessful_status_counts.get(
            "pending",
            pd.Series(dtype="int64"),
        )

        mixed_pattern_users = set(
            unsuccessful_counts[
                (unsuccessful_counts >= self.unsuccessful_minimum_count)
            ].index
        )

        mixed_pattern_users = {
            user_id
            for user_id in mixed_pattern_users
            if failed_counts.get(user_id, 0) > 0
            and pending_counts.get(user_id, 0) > 0
        }

        mixed_pattern = unsuccessful[
            unsuccessful["user_id"].isin(mixed_pattern_users)
        ]

        for _, row in mixed_pattern.iterrows():
            flag(
                row,
                "repeated_unsuccessful_transactions",
                (
                    "Customer has both failed and pending transactions, "
                    f"with at least {self.unsuccessful_minimum_count} "
                    "unsuccessful transactions in the supplied dataset."
                ),
            )

        # One transaction can trigger multiple rules. Keep each reason so
        # users can understand every applicable flag.
        anomalies.sort(
            key=lambda item: (
                str(item["transaction_date"]),
                str(item["transaction_id"]),
                item["rule"],
            )
        )

        return {
            "transaction_count": len(df),
            "anomaly_count": len(anomalies),
            "affected_customer_count": len(
                {item["user_id"] for item in anomalies}
            ),
            "rules_checked": 4,
            "anomalies": anomalies,
        }
