"""Tests for customer value and segmentation."""

import pandas as pd
import pytest

from app.analytics.customer_segmentation import CustomerSegmentation


@pytest.fixture
def sample_users():
    return pd.DataFrame({
        "user_id": [1, 2, 3, 4, 5],
        "email": [
            "a@example.com",
            "b@example.com",
            "c@example.com",
            "d@example.com",
            "e@example.com",
        ],
    })


@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "transaction_id": [101, 102, 103, 104, 105, 106],
        "user_id": [1, 1, 2, 3, 3, 4],
        "total_amount": [150.0, 100.0, 75.0, 20.0, 10.0, 500.0],
        "payment_status": [
            "completed",
            "completed",
            "completed",
            "completed",
            "failed",
            "pending",
        ],
        "transaction_date": [
            "2026-10-01",
            "2026-10-05",
            "2026-10-03",
            "2026-09-20",
            "2026-10-06",
            "2026-10-07",
        ],
    })


def test_customer_count_and_completed_value(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    assert result["customer_count"] == 5
    assert result["total_completed_transaction_value"] == 345.0


def test_completed_transaction_frequency(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    customers = {item["user_id"]: item for item in result["customers"]}

    assert customers[1]["completed_transaction_count"] == 2
    assert customers[2]["completed_transaction_count"] == 1
    assert customers[3]["completed_transaction_count"] == 1
    assert customers[4]["completed_transaction_count"] == 0
    assert customers[5]["completed_transaction_count"] == 0


def test_total_and_average_completed_value(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    customers = {item["user_id"]: item for item in result["customers"]}

    assert customers[1]["total_completed_value"] == 250.0
    assert customers[1]["average_completed_transaction_value"] == 125.0
    assert customers[2]["total_completed_value"] == 75.0
    assert customers[3]["total_completed_value"] == 20.0


def test_recency_is_calculated_from_reference_date(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    customers = {item["user_id"]: item for item in result["customers"]}

    assert customers[1]["recency_days"] == 5
    assert customers[2]["recency_days"] == 7
    assert customers[3]["recency_days"] == 20
    assert pd.isna(customers[4]["recency_days"])
    assert pd.isna(customers[5]["recency_days"])


def test_customer_segments_follow_configured_thresholds(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    customers = {item["user_id"]: item for item in result["customers"]}

    assert customers[1]["customer_segment"] == "High Value"
    assert customers[2]["customer_segment"] == "Regular Value"
    assert customers[3]["customer_segment"] == "Low Value"
    assert (
        customers[4]["customer_segment"]
        == "No Completed Transactions"
    )


def test_failed_and_pending_values_are_excluded(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    # Completed values: 150 + 100 + 75 + 20 = 345.
    # Failed and pending values are excluded.
    assert result["total_completed_transaction_value"] == 345.0


def test_segment_summary_counts_all_customers(
    sample_users, sample_transactions
):
    result = CustomerSegmentation().analyze(
        sample_users,
        sample_transactions,
        as_of_date="2026-10-10",
    )

    total_segment_customers = sum(
        item["customer_count"]
        for item in result["segment_summary"]
    )

    assert total_segment_customers == 5


def test_empty_customer_data_is_rejected(sample_transactions):
    with pytest.raises(ValueError, match="Customer dataset is empty"):
        CustomerSegmentation().analyze(
            pd.DataFrame(),
            sample_transactions,
            as_of_date="2026-10-10",
        )


def test_duplicate_customer_ids_are_rejected(
    sample_users, sample_transactions
):
    users = pd.concat(
        [sample_users, sample_users.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="Duplicate customer IDs"):
        CustomerSegmentation().analyze(
            users,
            sample_transactions,
            as_of_date="2026-10-10",
        )


def test_invalid_reference_date_before_transaction_is_rejected(
    sample_users, sample_transactions
):
    with pytest.raises(
        ValueError,
        match="Reference date must not precede a completed transaction",
    ):
        CustomerSegmentation().analyze(
            sample_users,
            sample_transactions,
            as_of_date="2026-09-01",
        )


def test_invalid_transaction_data_is_rejected(
    sample_users, sample_transactions
):
    transactions = sample_transactions.copy()
    transactions.loc[0, "total_amount"] = -10.0

    with pytest.raises(
        ValueError,
        match="Transaction amounts must not be negative",
    ):
        CustomerSegmentation().analyze(
            sample_users,
            transactions,
            as_of_date="2026-10-10",
        )


def test_invalid_threshold_configuration_is_rejected():
    with pytest.raises(
        ValueError,
        match="High-value threshold must be greater than or equal",
    ):
        CustomerSegmentation(
            high_value_threshold=50.0,
            regular_value_threshold=100.0,
        )

    with pytest.raises(
        ValueError,
        match="Regular-value threshold must not be negative",
    ):
        CustomerSegmentation(regular_value_threshold=-1.0)
