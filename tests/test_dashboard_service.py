from unittest.mock import Mock

import pandas as pd
import pytest

from app.ui.services.dashboard_service import DashboardService


@pytest.fixture
def dashboard_dependencies():
    reader = Mock()
    reader.read_transactions.return_value = pd.DataFrame(
        {"transaction_id": [1]}
    )
    reader.read_users.return_value = pd.DataFrame(
        {"user_id": [101]}
    )
    reader.read_products.return_value = pd.DataFrame(
        {"product_id": [201]}
    )

    revenue = Mock()
    revenue.analyze.return_value = {"completed_transaction_value": 150.0}

    payments = Mock()
    payments.analyze.return_value = {"completion_rate_pct": 75.0}

    customers = Mock()
    customers.analyze.return_value = {"total_customers": 1}

    segmentation = Mock()
    segmentation.analyze.return_value = {"customer_count": 1}

    anomalies = Mock()
    anomalies.analyze.return_value = {"anomaly_count": 0}

    products = Mock()
    products.analyze.return_value = {"total_products": 1}

    service = DashboardService(
        data_reader=reader,
        revenue_analytics=revenue,
        payment_analytics=payments,
        customer_analytics=customers,
        customer_segmentation=segmentation,
        anomaly_detector=anomalies,
        product_analytics=products,
    )

    return {
        "service": service,
        "reader": reader,
        "revenue": revenue,
        "payments": payments,
        "customers": customers,
        "segmentation": segmentation,
        "anomalies": anomalies,
        "products": products,
    }


def test_dashboard_reads_each_required_table_once(
    dashboard_dependencies,
):
    dependencies = dashboard_dependencies

    dependencies["service"].analyze()

    dependencies["reader"].read_transactions.assert_called_once_with()
    dependencies["reader"].read_users.assert_called_once_with()
    dependencies["reader"].read_products.assert_called_once_with()


def test_dashboard_passes_shared_dataframes_to_analytics(
    dashboard_dependencies,
):
    dependencies = dashboard_dependencies
    reader = dependencies["reader"]

    transactions = reader.read_transactions.return_value
    users = reader.read_users.return_value
    products = reader.read_products.return_value

    dependencies["service"].analyze()

    dependencies["revenue"].analyze.assert_called_once_with(transactions)
    dependencies["payments"].analyze.assert_called_once_with(transactions)

    dependencies["customers"].analyze.assert_called_once_with(
        users=users,
        transactions=transactions,
    )

    dependencies["segmentation"].analyze.assert_called_once_with(
        users=users,
        transactions=transactions,
    )

    dependencies["anomalies"].analyze.assert_called_once_with(transactions)
    dependencies["products"].analyze.assert_called_once_with(products)


def test_dashboard_returns_results_from_all_analytics_services(
    dashboard_dependencies,
):
    dependencies = dashboard_dependencies

    result = dependencies["service"].analyze()

    assert result == {
        "revenue": {"completed_transaction_value": 150.0},
        "payments": {"completion_rate_pct": 75.0},
        "customers": {"total_customers": 1},
        "segmentation": {"customer_count": 1},
        "anomalies": {"anomaly_count": 0},
        "products": {"total_products": 1},
    }


def test_dashboard_propagates_database_read_errors(
    dashboard_dependencies,
):
    dependencies = dashboard_dependencies

    dependencies["reader"].read_transactions.side_effect = RuntimeError(
        "Database connection failed"
    )

    with pytest.raises(RuntimeError, match="Database connection failed"):
        dependencies["service"].analyze()

    dependencies["reader"].read_users.assert_not_called()
    dependencies["reader"].read_products.assert_not_called()


def test_dashboard_propagates_analytics_validation_errors(
    dashboard_dependencies,
):
    dependencies = dashboard_dependencies

    dependencies["revenue"].analyze.side_effect = ValueError(
        "Transaction data validation failed"
    )

    with pytest.raises(
        ValueError,
        match="Transaction data validation failed",
    ):
        dependencies["service"].analyze()

    dependencies["payments"].analyze.assert_not_called()
