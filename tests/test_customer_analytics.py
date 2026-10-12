"""Tests for customer acquisition and geographic analytics."""

import pandas as pd
import pytest

from app.analytics.customer_analytics import CustomerAnalytics


@pytest.fixture
def sample_users():
    return pd.DataFrame({
        "user_id": [1, 2, 3, 4],
        "email": [
            "a@example.com",
            "b@example.com",
            "c@example.com",
            "d@example.com",
        ],
        "country": ["India", "India", "Canada", "UK"],
        "signup_date": [
            "2026-01-01",
            "2026-01-01",
            "2026-02-15",
            "2026-03-10",
        ],
    })


@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "transaction_id": [101, 102, 103, 104],
        "user_id": [1, 2, 1, 3],
        "total_amount": [100.00, 50.00, 25.00, 75.00],
        "payment_status": [
            "completed", "failed", "pending", "completed"
        ],
        "transaction_date": [
            "2026-01-05",
            "2026-01-10",
            "2026-02-01",
            "2026-02-20",
        ],
    })


def test_customer_totals_and_activity(sample_users, sample_transactions):
    result = CustomerAnalytics().analyze(sample_users, sample_transactions)

    assert result["total_customers"] == 4
    assert result["countries_represented"] == 3
    assert result["customers_with_transactions"] == 3
    assert result["customers_without_transactions"] == 1
    assert result["customer_activity_rate_pct"] == 75.0


def test_country_distribution(sample_users, sample_transactions):
    result = CustomerAnalytics().analyze(sample_users, sample_transactions)
    distribution = {
        item["country"]: item for item in result["country_distribution"]
    }

    assert distribution["India"]["customer_count"] == 2
    assert distribution["India"]["customer_share_pct"] == 50.0
    assert distribution["Canada"]["customer_count"] == 1
    assert distribution["UK"]["customer_count"] == 1


def test_signup_trends(sample_users, sample_transactions):
    result = CustomerAnalytics().analyze(sample_users, sample_transactions)
    trends = {
        item["date"]: item["new_customers"]
        for item in result["signup_trends"]
    }

    assert trends == {
        "2026-01-01": 2,
        "2026-02-15": 1,
        "2026-03-10": 1,
    }


def test_transaction_performance_by_country(
    sample_users, sample_transactions
):
    result = CustomerAnalytics().analyze(sample_users, sample_transactions)
    countries = {
        item["country"]: item
        for item in result["transaction_performance_by_country"]
    }

    assert countries["India"]["transaction_count"] == 3
    assert countries["India"]["transaction_value"] == 175.0
    assert countries["India"]["completed"] == 1
    assert countries["India"]["failed"] == 1
    assert countries["India"]["pending"] == 1

    assert countries["Canada"]["transaction_count"] == 1
    assert countries["Canada"]["transaction_value"] == 75.0
    assert countries["Canada"]["completed"] == 1


def test_unmatched_transactions_are_reported(
    sample_users, sample_transactions
):
    extra = pd.DataFrame({
        "transaction_id": [105],
        "user_id": [999],
        "total_amount": [20.0],
        "payment_status": ["completed"],
        "transaction_date": ["2026-03-01"],
    })
    transactions = pd.concat(
        [sample_transactions, extra], ignore_index=True
    )

    result = CustomerAnalytics().analyze(sample_users, transactions)

    assert result["unmatched_transaction_count"] == 1
    reported_count = sum(
        item["transaction_count"]
        for item in result["transaction_performance_by_country"]
    )
    assert reported_count == 4


def test_empty_customer_data_is_rejected(sample_transactions):
    with pytest.raises(ValueError, match="Customer dataset is empty"):
        CustomerAnalytics().analyze(pd.DataFrame(), sample_transactions)


def test_duplicate_customer_ids_are_rejected(
    sample_users, sample_transactions
):
    users = pd.concat(
        [sample_users, sample_users.iloc[[0]]], ignore_index=True
    )

    with pytest.raises(ValueError, match="Duplicate customer IDs"):
        CustomerAnalytics().analyze(users, sample_transactions)


def test_missing_customer_column_is_rejected(
    sample_users, sample_transactions
):
    users = sample_users.drop(columns=["signup_date"])

    with pytest.raises(
        ValueError, match="Missing required customer columns"
    ):
        CustomerAnalytics().analyze(users, sample_transactions)


def test_invalid_signup_date_is_rejected(
    sample_users, sample_transactions
):
    users = sample_users.copy()
    users.loc[0, "signup_date"] = "not-a-date"

    with pytest.raises(
        ValueError,
        match="Customer signup dates must be present and valid",
    ):
        CustomerAnalytics().analyze(users, sample_transactions)


def test_invalid_transactions_are_rejected(
    sample_users, sample_transactions
):
    transactions = sample_transactions.copy()
    transactions.loc[0, "total_amount"] = -100

    with pytest.raises(
        ValueError,
        match="Transaction amounts must not be negative",
    ):
        CustomerAnalytics().analyze(sample_users, transactions)


def test_missing_country_is_reported_as_unknown(
    sample_users, sample_transactions
):
    users = sample_users.copy()
    users.loc[0, "country"] = None

    result = CustomerAnalytics().analyze(users, sample_transactions)
    distribution = {
        item["country"]: item for item in result["country_distribution"]
    }

    assert "Unknown" in distribution
    assert distribution["Unknown"]["customer_count"] == 1
    assert any(
        "no country recorded" in warning
        for warning in result["validation_warnings"]
    )
