"""Tests for revenue analytics."""

import pandas as pd
import pytest

from app.analytics.revenue_analytics import RevenueAnalytics


@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "transaction_id": [1, 2, 3, 4, 5],
            "user_id": [101, 102, 103, 104, 105],
            "total_amount": [100.00, 10.00, 200.00, 50.00, 120.00],
            "payment_status": [
                "completed",
                "failed",
                "completed",
                "pending",
                "completed",
            ],
            "transaction_date": pd.to_datetime(
                [
                    "2026-01-10",
                    "2026-01-15",
                    "2026-02-12",
                    "2026-02-20",
                    "2026-03-05",
                ]
            ),
        }
    )


def test_transaction_overview(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    assert result["total_transactions"] == 5
    assert result["total_transaction_value"] == 480.00


def test_completed_transaction_metrics(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    assert result["completed_transaction_count"] == 3
    assert result["completed_transaction_value"] == 420.00


def test_failed_transaction_metrics(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    assert result["failed_transaction_count"] == 1
    assert result["failed_transaction_value"] == 10.00


def test_pending_transaction_metrics(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    assert result["pending_transaction_count"] == 1
    assert result["pending_transaction_value"] == 50.00


def test_payment_status_breakdown(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    breakdown = {
        item["payment_status"]: item
        for item in result["payment_status_breakdown"]
    }

    assert breakdown["completed"]["transaction_count"] == 3
    assert breakdown["completed"]["transaction_value"] == 420.00
    assert breakdown["failed"]["transaction_count"] == 1
    assert breakdown["failed"]["transaction_value"] == 10.00
    assert breakdown["pending"]["transaction_count"] == 1
    assert breakdown["pending"]["transaction_value"] == 50.00


def test_monthly_trend_includes_completed_transactions_only(
    sample_transactions,
):
    result = RevenueAnalytics().analyze(sample_transactions)

    trend = result["revenue_trend"]

    assert trend == [
        {
            "period": "2026-01",
            "completed_transaction_count": 1,
            "completed_transaction_value": 100.00,
        },
        {
            "period": "2026-02",
            "completed_transaction_count": 1,
            "completed_transaction_value": 200.00,
        },
        {
            "period": "2026-03",
            "completed_transaction_count": 1,
            "completed_transaction_value": 120.00,
        },
    ]


def test_monthly_trend_is_chronologically_sorted(sample_transactions):
    result = RevenueAnalytics().analyze(sample_transactions)

    periods = [
        item["period"]
        for item in result["revenue_trend"]
    ]

    assert periods == sorted(periods)


def test_failed_and_pending_values_are_not_counted_as_completed(
    sample_transactions,
):
    result = RevenueAnalytics().analyze(sample_transactions)

    assert result["total_transaction_value"] == 480.00
    assert result["completed_transaction_value"] == 420.00
    assert (
        result["failed_transaction_value"]
        + result["pending_transaction_value"]
    ) == 60.00


def test_empty_transactions_return_zero_metrics():
    transactions = pd.DataFrame(
        columns=[
            "transaction_id",
            "user_id",
            "total_amount",
            "payment_status",
            "transaction_date",
        ]
    )

    result = RevenueAnalytics().analyze(transactions)

    assert result["total_transactions"] == 0
    assert result["total_transaction_value"] == 0.00
    assert result["completed_transaction_count"] == 0
    assert result["completed_transaction_value"] == 0.00
    assert result["failed_transaction_count"] == 0
    assert result["failed_transaction_value"] == 0.00
    assert result["pending_transaction_count"] == 0
    assert result["pending_transaction_value"] == 0.00
    assert result["payment_status_breakdown"] == []
    assert result["revenue_trend"] == []


def test_missing_required_column_is_rejected(sample_transactions):
    transactions = sample_transactions.drop(columns=["total_amount"])

    with pytest.raises(ValueError, match="Missing required transaction columns"):
        RevenueAnalytics().analyze(transactions)


def test_invalid_payment_status_is_rejected(sample_transactions):
    transactions = sample_transactions.copy()
    transactions.loc[0, "payment_status"] = "unknown"

    with pytest.raises(ValueError, match="validation"):
        RevenueAnalytics().analyze(transactions)


@pytest.mark.parametrize("invalid_amount", [-1.0, None, "invalid"])
def test_invalid_transaction_amount_is_rejected(
    sample_transactions,
    invalid_amount,
):
    transactions = sample_transactions.astype(
        {"total_amount": "object"}
    ).copy()
    transactions.loc[0, "total_amount"] = invalid_amount

    with pytest.raises(ValueError, match="validation"):
        RevenueAnalytics().analyze(transactions)


def test_invalid_transaction_date_is_rejected(sample_transactions):
    transactions = sample_transactions.copy()
    transactions["transaction_date"] = transactions[
        "transaction_date"
    ].astype("object")
    transactions.loc[0, "transaction_date"] = "not-a-date"

    with pytest.raises(ValueError, match="validation"):
        RevenueAnalytics().analyze(transactions)


def test_duplicate_transaction_ids_are_rejected(sample_transactions):
    transactions = sample_transactions.copy()
    transactions.loc[1, "transaction_id"] = 1

    with pytest.raises(ValueError, match="validation"):
        RevenueAnalytics().analyze(transactions)


def test_input_dataframe_is_not_modified(sample_transactions):
    original = sample_transactions.copy(deep=True)

    RevenueAnalytics().analyze(sample_transactions)

    pd.testing.assert_frame_equal(sample_transactions, original)


def test_non_dataframe_input_is_rejected():
    with pytest.raises(ValueError, match="Pandas DataFrame"):
        RevenueAnalytics().analyze([{"transaction_id": 1}])
