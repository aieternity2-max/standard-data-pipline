"""Customer acquisition and geographic business analytics."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader
from app.analytics.validators import (
    AnalyticsValidationResult,
    TransactionDataValidator,
)


class CustomerAnalytics:
    """Calculate customer acquisition, activity, and geographic KPIs."""

    REQUIRED_USER_COLUMNS = {
        "user_id",
        "country",
        "signup_date",
    }

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
        transaction_validator: TransactionDataValidator | None = None,
    ) -> None:
        self.data_reader = data_reader or StructuredDataReader()
        self.transaction_validator = (
            transaction_validator or TransactionDataValidator()
        )

    def _validate_users(
        self,
        dataframe: pd.DataFrame,
    ) -> AnalyticsValidationResult:
        """Validate customer data before calculating KPIs."""

        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(dataframe, pd.DataFrame):
            return AnalyticsValidationResult(
                is_valid=False,
                errors=["Customer input must be a Pandas DataFrame."],
            )

        if dataframe.empty:
            return AnalyticsValidationResult(
                is_valid=False,
                errors=["Customer dataset is empty."],
            )

        missing_columns = self.REQUIRED_USER_COLUMNS - set(dataframe.columns)

        if missing_columns:
            errors.append(
                "Missing required customer columns: "
                + ", ".join(sorted(missing_columns))
            )

            return AnalyticsValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
            )

        if dataframe["user_id"].isna().any():
            errors.append("Customer IDs must not be missing.")

        if dataframe["user_id"].duplicated().any():
            errors.append("Duplicate customer IDs were found.")

        countries = dataframe["country"]

        if countries.isna().any():
            warnings.append(
                "Some customers have no country recorded."
            )

        if countries.astype("string").str.strip().eq("").any():
            warnings.append(
                "Some customers have an empty country value."
            )

        signup_dates = pd.to_datetime(
            dataframe["signup_date"],
            errors="coerce",
            format="mixed",
        )

        if signup_dates.isna().any():
            errors.append(
                "Customer signup dates must be present and valid."
            )

        return AnalyticsValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )

    def analyze(
        self,
        users: pd.DataFrame | None = None,
        transactions: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """
        Calculate customer acquisition and geographic metrics.

        Optional DataFrames allow isolated testing without a database.
        Missing DataFrames are read from MySQL.
        """

        if users is None:
            users = self.data_reader.read_users()

        user_validation = self._validate_users(users)

        if not user_validation.is_valid:
            raise ValueError(
                "Customer data validation failed: "
                + "; ".join(user_validation.errors)
            )

        if transactions is None:
            transactions = self.data_reader.read_transactions()

        transaction_validation = self.transaction_validator.validate(
            transactions
        )

        if not transaction_validation.is_valid:
            raise ValueError(
                "Transaction data validation failed: "
                + "; ".join(transaction_validation.errors)
            )

        customers = users.copy()
        payments = transactions.copy()

        customers["country"] = (
            customers["country"]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
            .fillna("Unknown")
        )

        customers["signup_date"] = pd.to_datetime(
            customers["signup_date"],
            errors="raise",
            format="mixed",
        )

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

        # Aggregate sign-ups by calendar date.
        customers["signup_day"] = (
            customers["signup_date"].dt.strftime("%Y-%m-%d")
        )

        signup_trends = (
            customers.groupby("signup_day")
            .size()
            .rename("new_customers")
            .reset_index()
            .rename(columns={"signup_day": "date"})
            .to_dict(orient="records")
        )

        # Geographic customer distribution.
        total_customers = len(customers)

        country_distribution = (
            customers.groupby("country")
            .agg(customer_count=("user_id", "nunique"))
            .reset_index()
            .sort_values(
                ["customer_count", "country"],
                ascending=[False, True],
            )
        )

        country_distribution["customer_share_pct"] = (
            country_distribution["customer_count"]
            .div(total_customers)
            .mul(100)
            .round(2)
        )

        # Customer activity is based on the presence of transactions,
        # irrespective of payment status.
        active_user_ids = set(payments["user_id"].dropna())
        customer_ids = set(customers["user_id"])

        customers_with_transactions = len(
            customer_ids.intersection(active_user_ids)
        )

        customers_without_transactions = (
            total_customers - customers_with_transactions
        )

        # Join transactions to known customers only.
        # Unmatched transactions are reported separately.
        customer_lookup = customers[
            ["user_id", "country"]
        ].drop_duplicates("user_id")

        enriched_transactions = payments.merge(
            customer_lookup,
            on="user_id",
            how="left",
            validate="many_to_one",
            indicator=True,
        )

        unmatched_transaction_count = int(
            enriched_transactions["_merge"].eq("left_only").sum()
        )

        matched_transactions = enriched_transactions[
            enriched_transactions["_merge"].eq("both")
        ].copy()

        matched_transactions["country"] = (
            matched_transactions["country"]
            .fillna("Unknown")
        )

        geographic_transactions = (
            matched_transactions.groupby("country")
            .agg(
                transaction_count=("transaction_id", "count"),
                transaction_value=("total_amount", "sum"),
            )
            .reset_index()
        )

        geographic_transactions["transaction_value"] = (
            geographic_transactions["transaction_value"].round(2)
        )

        geographic_payments = (
            matched_transactions.pivot_table(
                index="country",
                columns="payment_status",
                values="transaction_id",
                aggfunc="count",
                fill_value=0,
            )
            .reindex(
                columns=["completed", "failed", "pending"],
                fill_value=0,
            )
            .reset_index()
        )

        geographic_payments.columns.name = None

        payment_country_summary = geographic_transactions.merge(
            geographic_payments,
            on="country",
            how="left",
            validate="one_to_one",
        )

        for status in ["completed", "failed", "pending"]:
            payment_country_summary[status] = (
                payment_country_summary[status].astype(int)
            )

        payment_country_summary = (
            payment_country_summary.sort_values(
                "country"
            ).to_dict(orient="records")
        )

        return {
            "total_customers": total_customers,
            "countries_represented": int(
                customers["country"].nunique()
            ),
            "customers_with_transactions": (
                customers_with_transactions
            ),
            "customers_without_transactions": (
                customers_without_transactions
            ),
            "customer_activity_rate_pct": round(
                customers_with_transactions
                / total_customers
                * 100,
                2,
            ),
            "unmatched_transaction_count": (
                unmatched_transaction_count
            ),
            "signup_trends": signup_trends,
            "country_distribution": (
                country_distribution.to_dict(orient="records")
            ),
            "transaction_performance_by_country": (
                payment_country_summary
            ),
            "validation_warnings": (
                user_validation.warnings
                + transaction_validation.warnings
            ),
        }