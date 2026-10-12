import pandas as pd
import pytest

from app.analytics.transaction_anomalies import TransactionAnomalyDetector


@pytest.fixture
def transactions():
    return pd.DataFrame(
        [
            {
                "transaction_id": 101,
                "user_id": 1,
                "total_amount": 50.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 10:00:00",
            },
            {
                "transaction_id": 102,
                "user_id": 1,
                "total_amount": 75.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 10:03:00",
            },
            {
                "transaction_id": 103,
                "user_id": 2,
                "total_amount": 600.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 11:00:00",
            },
            {
                "transaction_id": 104,
                "user_id": 3,
                "total_amount": 20.00,
                "payment_status": "failed",
                "transaction_date": "2026-10-10 12:00:00",
            },
            {
                "transaction_id": 105,
                "user_id": 3,
                "total_amount": 25.00,
                "payment_status": "failed",
                "transaction_date": "2026-10-10 12:02:00",
            },
            {
                "transaction_id": 106,
                "user_id": 4,
                "total_amount": 30.00,
                "payment_status": "pending",
                "transaction_date": "2026-10-10 13:00:00",
            },
            {
                "transaction_id": 107,
                "user_id": 4,
                "total_amount": 35.00,
                "payment_status": "failed",
                "transaction_date": "2026-10-10 13:03:00",
            },
            {
                "transaction_id": 108,
                "user_id": 5,
                "total_amount": 40.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 14:00:00",
            },
        ]
    )


def test_detects_high_value_transactions(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=500.00,
    )

    result = detector.analyze(transactions)

    high_value = [
        item
        for item in result["anomalies"]
        if item["rule"] == "high_value_transaction"
    ]

    assert [item["transaction_id"] for item in high_value] == [103]


def test_detects_rapid_repeated_transactions(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=1000.00,
        repeat_window_minutes=5,
        repeat_minimum_count=2,
    )

    result = detector.analyze(transactions)

    repeated_ids = {
        item["transaction_id"]
        for item in result["anomalies"]
        if item["rule"] == "rapid_repeated_transactions"
    }

    assert repeated_ids == {101, 102, 104, 105, 106, 107}


def test_detects_repeated_failed_transactions(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=1000.00,
        repeat_window_minutes=5,
        repeat_minimum_count=3,
        failed_minimum_count=2,
    )

    result = detector.analyze(transactions)

    failed_ids = {
        item["transaction_id"]
        for item in result["anomalies"]
        if item["rule"] == "repeated_failed_transactions"
    }

    assert failed_ids == {104, 105}


def test_detects_repeated_failed_and_pending_patterns(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=1000.00,
        repeat_window_minutes=5,
        repeat_minimum_count=3,
        failed_minimum_count=3,
        unsuccessful_minimum_count=2,
    )

    result = detector.analyze(transactions)

    flagged_ids = {
        item["transaction_id"]
        for item in result["anomalies"]
        if item["rule"] == "repeated_unsuccessful_transactions"
    }

    assert flagged_ids == {106, 107}


def test_reports_summary_and_unique_affected_customers(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=500.00,
        repeat_window_minutes=5,
        repeat_minimum_count=2,
        failed_minimum_count=2,
        unsuccessful_minimum_count=2,
    )

    result = detector.analyze(transactions)

    assert result["transaction_count"] == 8
    assert result["anomaly_count"] == len(result["anomalies"])
    assert result["affected_customer_count"] == len(
        {
            item["user_id"]
            for item in result["anomalies"]
        }
    )
    assert result["rules_checked"] == 4


def test_does_not_flag_normal_transactions():
    data = pd.DataFrame(
        [
            {
                "transaction_id": 201,
                "user_id": 10,
                "total_amount": 25.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 10:00:00",
            },
            {
                "transaction_id": 202,
                "user_id": 11,
                "total_amount": 35.00,
                "payment_status": "completed",
                "transaction_date": "2026-10-10 11:00:00",
            },
        ]
    )

    result = TransactionAnomalyDetector().analyze(data)

    assert result["anomalies"] == []
    assert result["anomaly_count"] == 0
    assert result["affected_customer_count"] == 0


def test_high_value_threshold_is_inclusive(transactions):
    detector = TransactionAnomalyDetector(
        high_value_threshold=600.00,
        repeat_window_minutes=1,
        repeat_minimum_count=3,
        failed_minimum_count=3,
        unsuccessful_minimum_count=3,
    )

    result = detector.analyze(transactions)

    high_value_ids = {
        item["transaction_id"]
        for item in result["anomalies"]
        if item["rule"] == "high_value_transaction"
    }

    assert high_value_ids == {103}


def test_rejects_invalid_transaction_data(transactions):
    invalid = transactions.copy()
    invalid.loc[0, "total_amount"] = -10.00

    with pytest.raises(ValueError, match="validation failed"):
        TransactionAnomalyDetector().analyze(invalid)


def test_rejects_empty_transaction_data():
    empty = pd.DataFrame(
        columns=[
            "transaction_id",
            "user_id",
            "total_amount",
            "payment_status",
            "transaction_date",
        ]
    )

    with pytest.raises(ValueError, match="validation failed"):
        TransactionAnomalyDetector().analyze(empty)


@pytest.mark.parametrize(
    ("configuration", "message"),
    [
        ({"high_value_threshold": 0}, "high-value threshold"),
        ({"repeat_window_minutes": 0}, "repeat window"),
        ({"repeat_minimum_count": 1}, "repeat minimum count"),
        ({"failed_minimum_count": 1}, "failed minimum count"),
        ({"unsuccessful_minimum_count": 1}, "unsuccessful minimum count"),
    ],
)
def test_rejects_invalid_configuration(configuration, message):
    with pytest.raises(ValueError, match=message):
        TransactionAnomalyDetector(**configuration)
