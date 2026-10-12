import pandas as pd
import pytest

from app.analytics.payment_analytics import PaymentAnalytics
from app.analytics.validators import TransactionDataValidator


@pytest.fixture
def transactions():
    return pd.DataFrame(
        [
            {
                "transaction_id": 101,
                "user_id": 1,
                "total_amount": 49.99,
                "payment_status": "completed",
                "transaction_date": "2026-01-16 10:00:00",
            },
            {
                "transaction_id": 102,
                "user_id": 2,
                "total_amount": 120.50,
                "payment_status": "completed",
                "transaction_date": "2026-02-22 14:30:00",
            },
            {
                "transaction_id": 103,
                "user_id": 3,
                "total_amount": 15.00,
                "payment_status": "failed",
                "transaction_date": "2026-03-11 09:15:00",
            },
            {
                "transaction_id": 104,
                "user_id": 4,
                "total_amount": 250.00,
                "payment_status": "completed",
                "transaction_date": "2026-04-06 18:45:00",
            },
            {
                "transaction_id": 105,
                "user_id": 5,
                "total_amount": 89.95,
                "payment_status": "pending",
                "transaction_date": "2026-05-13 11:20:00",
            },
        ]
    )


def test_payment_kpis(transactions):
    result = PaymentAnalytics().analyze(transactions)

    assert result["total_transactions"] == 5
    assert result["total_transaction_value"] == 525.44

    assert result["completed_transactions"] == 3
    assert result["failed_transactions"] == 1
    assert result["pending_transactions"] == 1

    assert result["completion_rate_pct"] == 60.0
    assert result["failure_rate_pct"] == 20.0
    assert result["pending_rate_pct"] == 20.0

    assert result["completed_transaction_value"] == 420.49
    assert result["failed_transaction_value"] == 15.00
    assert result["pending_transaction_value"] == 89.95

    assert result["potentially_affected_payment_value"] == 104.95


def test_empty_dataset_is_rejected():
    empty = pd.DataFrame(
        columns=[
            "transaction_id",
            "user_id",
            "total_amount",
            "payment_status",
            "transaction_date",
        ]
    )

    result = TransactionDataValidator().validate(empty)

    assert result.is_valid is False
    assert any("empty" in error.lower() for error in result.errors)


def test_missing_required_column_is_rejected(transactions):
    invalid = transactions.drop(columns=["payment_status"])

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("payment_status" in error for error in result.errors)


def test_duplicate_transaction_ids_are_rejected(transactions):
    invalid = pd.concat(
        [transactions, transactions.iloc[[0]]],
        ignore_index=True,
    )

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("duplicate" in error.lower() for error in result.errors)


def test_negative_transaction_amount_is_rejected(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "total_amount"] = -10.00

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("negative" in error.lower() for error in result.errors)


def test_missing_payment_status_is_rejected(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "payment_status"] = None

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("missing" in error.lower() for error in result.errors)


def test_unsupported_payment_status_is_rejected(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "payment_status"] = "unknown_status"

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("unsupported" in error.lower() for error in result.errors)


def test_invalid_transaction_date_is_rejected(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "transaction_date"] = "not-a-date"

    result = TransactionDataValidator().validate(invalid)

    assert result.is_valid is False
    assert any("date" in error.lower() for error in result.errors)


def test_daily_trends(transactions):
    result = PaymentAnalytics().analyze(transactions)

    assert len(result["daily_trends"]) == 5
    assert result["daily_trends"][0]["date"] == "2026-01-16"
    assert result["daily_trends"][0]["transaction_count"] == 1
    assert result["daily_trends"][0]["transaction_value"] == 49.99


def test_invalid_data_is_not_analysed(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "total_amount"] = -10.00

    with pytest.raises(ValueError, match="validation failed"):
        PaymentAnalytics().analyze(invalid)