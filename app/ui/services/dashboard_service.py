"""Coordinate existing analytics services for the InsightSphere dashboard."""

from typing import Any

from app.analytics.customer_analytics import CustomerAnalytics
from app.analytics.customer_segmentation import CustomerSegmentation
from app.analytics.data_reader import StructuredDataReader
from app.analytics.payment_analytics import PaymentAnalytics
from app.analytics.product_analytics import ProductAnalytics
from app.analytics.revenue_analytics import RevenueAnalytics
from app.analytics.transaction_anomalies import TransactionAnomalyDetector


class DashboardService:
    """Load business data once and coordinate dashboard analytics."""

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
        revenue_analytics: RevenueAnalytics | None = None,
        payment_analytics: PaymentAnalytics | None = None,
        customer_analytics: CustomerAnalytics | None = None,
        customer_segmentation: CustomerSegmentation | None = None,
        anomaly_detector: TransactionAnomalyDetector | None = None,
        product_analytics: ProductAnalytics | None = None,
    ) -> None:
        self.data_reader = data_reader or StructuredDataReader()
        self.revenue_analytics = revenue_analytics or RevenueAnalytics(
            data_reader=self.data_reader
        )
        self.payment_analytics = payment_analytics or PaymentAnalytics(
            data_reader=self.data_reader
        )
        self.customer_analytics = customer_analytics or CustomerAnalytics(
            data_reader=self.data_reader
        )
        self.customer_segmentation = (
            customer_segmentation
            or CustomerSegmentation(data_reader=self.data_reader)
        )
        self.anomaly_detector = anomaly_detector or (
            TransactionAnomalyDetector(data_reader=self.data_reader)
        )
        self.product_analytics = product_analytics or ProductAnalytics(
            data_reader=self.data_reader
        )

    def analyze(self) -> dict[str, Any]:
        """Read the required tables once and calculate dashboard results."""

        transactions = self.data_reader.read_transactions()
        users = self.data_reader.read_users()
        products = self.data_reader.read_products()

        return {
            "revenue": self.revenue_analytics.analyze(transactions),
            "payments": self.payment_analytics.analyze(transactions),
            "customers": self.customer_analytics.analyze(
                users=users,
                transactions=transactions,
            ),
            "segmentation": self.customer_segmentation.analyze(
                users=users,
                transactions=transactions,
            ),
            "anomalies": self.anomaly_detector.analyze(transactions),
            "products": self.product_analytics.analyze(products),
        }