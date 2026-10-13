"""Business analytics dashboard for InsightSphere."""

from typing import Any

import pandas as pd
import streamlit as st

from app.ui.services.dashboard_service import DashboardService


def _format_currency(value: Any) -> str:
    """Format a numeric value as Indian rupees."""
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def _render_table(records: Any, empty_message: str) -> None:
    """Render records as a table, or show an empty-state message."""
    if not records:
        st.info(empty_message)
        return

    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)


def _chart_frame(
    records: Any,
    x_column: str,
    y_columns: list[str],
) -> pd.DataFrame:
    """Return validated chart data, or an empty DataFrame."""
    if not records:
        return pd.DataFrame()

    dataframe = pd.DataFrame(records)
    available_columns = [
        column for column in y_columns if column in dataframe.columns
    ]

    if x_column not in dataframe.columns or not available_columns:
        return pd.DataFrame()

    chart_data = dataframe[[x_column, *available_columns]].copy()
    chart_data = chart_data.set_index(x_column)

    for column in available_columns:
        chart_data[column] = pd.to_numeric(chart_data[column], errors="coerce")

    return chart_data.dropna(how="all")


def _render_line_chart(
    records: Any,
    x_column: str,
    y_columns: list[str],
    empty_message: str,
) -> None:
    """Render a native Streamlit line chart when usable data exists."""
    chart_data = _chart_frame(records, x_column, y_columns)
    if chart_data.empty:
        st.info(empty_message)
        return
    st.line_chart(chart_data, use_container_width=True)


def _render_bar_chart(
    records: Any,
    x_column: str,
    y_column: str,
    empty_message: str,
) -> None:
    """Render a native Streamlit bar chart when usable data exists."""
    chart_data = _chart_frame(records, x_column, [y_column])
    if chart_data.empty:
        st.info(empty_message)
        return
    st.bar_chart(chart_data, use_container_width=True)


def render_dashboards(
    dashboard_service: DashboardService | None = None,
) -> None:
    """Render business analytics using the existing analytics services."""

    st.title("Business Dashboards")
    st.caption(
        "Explore revenue, payment performance, customer behaviour, "
        "transaction anomalies, and product catalogue health."
    )

    if st.button("Refresh dashboard", type="primary"):
        st.session_state.pop("insightsphere_dashboard_results", None)

    if "insightsphere_dashboard_results" not in st.session_state:
        with st.spinner("Loading business analytics..."):
            try:
                service = dashboard_service or DashboardService()
                st.session_state["insightsphere_dashboard_results"] = (
                    service.analyze()
                )
            except Exception as exc:
                st.error(
                    "Unable to load dashboard data. Check the database "
                    "connection and analytics validation."
                )
                st.caption(f"Details: {exc}")
                return

    results = st.session_state["insightsphere_dashboard_results"]
    revenue = results["revenue"]
    payments = results["payments"]
    customers = results["customers"]
    segmentation = results["segmentation"]
    anomalies = results["anomalies"]
    products = results["products"]

    # Payment overview: clean, light dashboard cards and chart panels.
    st.subheader("Payment & Transaction Analysis")
    metric_columns = st.columns(5)
    metric_columns[0].metric(
        "Completed transaction value",
        _format_currency(revenue.get("completed_transaction_value", 0)),
    )
    metric_columns[1].metric(
        "Total transactions",
        f"{payments.get('total_transactions', 0):,}",
    )
    metric_columns[2].metric(
        "Completion rate",
        f"{payments.get('completion_rate_pct', 0):.2f}%",
    )
    metric_columns[3].metric(
        "Failed transactions",
        f"{payments.get('failed_transactions', 0):,}",
    )
    metric_columns[4].metric(
        "Pending transactions",
        f"{payments.get('pending_transactions', 0):,}",
    )

    st.caption(
        "Failed and pending transaction values are potential leakage "
        "indicators, not confirmed financial losses."
    )

    payment_left, payment_right = st.columns([1.55, 1])
    with payment_left:
        st.markdown("#### Monthly completed transaction value")
        _render_line_chart(
            revenue.get("revenue_trend", []),
            x_column="period",
            y_columns=["completed_transaction_value"],
            empty_message="No monthly revenue trend is available.",
        )
        st.markdown("#### Daily transaction activity")
        # PaymentAnalytics returns daily trend records with the key `date`.
        daily_trends = payments.get("daily_trends", [])
        daily_frame = _chart_frame(
            daily_trends,
            "date",
            ["transaction_value", "transaction_count"],
        )
        if daily_frame.empty:
            st.info("No daily payment trend is available.")
        else:
            st.bar_chart(
                daily_frame[["transaction_value"]],
                use_container_width=True,
            )
            st.line_chart(
                daily_frame[["transaction_count"]],
                use_container_width=True,
            )

    with payment_right:
        st.markdown("#### Transaction status")
        status_counts = [
            {"status": "Completed", "count": payments.get("completed_transactions", 0)},
            {"status": "Pending", "count": payments.get("pending_transactions", 0)},
            {"status": "Failed", "count": payments.get("failed_transactions", 0)},
        ]
        _render_bar_chart(
            status_counts,
            x_column="status",
            y_column="count",
            empty_message="No transaction status data is available.",
        )

        st.markdown("#### Transaction value by status")
        value_by_status = [
            {
                "status": "Completed",
                "value": revenue.get("completed_transaction_value", 0),
            },
            {
                "status": "Pending",
                "value": payments.get("pending_transaction_value", 0),
            },
            {
                "status": "Failed",
                "value": payments.get("failed_transaction_value", 0),
            },
        ]
        _render_bar_chart(
            value_by_status,
            x_column="status",
            y_column="value",
            empty_message="No transaction value breakdown is available.",
        )

    st.divider()

    # Customer analytics: summary, signup trend, geography and segments.
    st.subheader("Customer Analytics")
    customer_columns = st.columns(4)
    customer_columns[0].metric(
        "Total customers", f"{customers.get('total_customers', 0):,}"
    )
    customer_columns[1].metric(
        "Customers with transactions",
        f"{customers.get('customers_with_transactions', 0):,}",
    )
    customer_columns[2].metric(
        "Customers without transactions",
        f"{customers.get('customers_without_transactions', 0):,}",
    )
    customer_columns[3].metric(
        "Countries represented", f"{customers.get('countries_represented', 0):,}"
    )

    customer_left, customer_right = st.columns([1, 1.2])
    with customer_left:
        st.markdown("#### Customers with vs. without transactions")
        activity_counts = [
            {
                "customer_activity": "With transactions",
                "customers": customers.get("customers_with_transactions", 0),
            },
            {
                "customer_activity": "Without transactions",
                "customers": customers.get("customers_without_transactions", 0),
            },
        ]
        _render_bar_chart(
            activity_counts,
            x_column="customer_activity",
            y_column="customers",
            empty_message="No customer activity data is available.",
        )

        st.markdown("#### New customer signups")
        _render_line_chart(
            customers.get("signup_trends", []),
            x_column="date",
            y_columns=["new_customers"],
            empty_message="No signup trend is available.",
        )

    with customer_right:
        st.markdown("#### Customers by country")
        country_distribution = customers.get("country_distribution", [])
        _render_bar_chart(
            country_distribution,
            x_column="country",
            y_column="customer_count",
            empty_message="No customer geography data is available.",
        )
        _render_table(
            country_distribution,
            "No customer geography data is available.",
        )

    st.divider()
    st.subheader("Customer Segmentation")
    segment_columns = st.columns(3)
    segment_columns[0].metric(
        "Customers analysed", f"{segmentation.get('customer_count', 0):,}"
    )
    segment_columns[1].metric(
        "Completed transaction value",
        _format_currency(segmentation.get("total_completed_transaction_value", 0)),
    )
    segment_columns[2].metric(
        "Segmentation as of", str(segmentation.get("as_of_date", "N/A"))
    )

    segment_summary = segmentation.get("segment_summary", [])
    segment_left, segment_right = st.columns(2)
    with segment_left:
        st.markdown("#### Customers by segment")
        _render_bar_chart(
            segment_summary,
            x_column="customer_segment",
            y_column="customer_count",
            empty_message="No customer segment summary is available.",
        )
    with segment_right:
        st.markdown("#### Completed value by segment")
        _render_bar_chart(
            segment_summary,
            x_column="customer_segment",
            y_column="total_completed_value",
            empty_message="No completed value by segment is available.",
        )
    _render_table(
        segment_summary,
        "No customer segment summary is available.",
    )
    st.caption(
        "Segments are assigned using completed transaction value thresholds; "
        "they are not a predictive customer lifetime value model."
    )

    st.divider()
    st.subheader("Transaction Anomaly Indicators")
    anomaly_columns = st.columns(3)
    anomaly_columns[0].metric(
        "Transactions analysed", f"{anomalies.get('transaction_count', 0):,}"
    )
    anomaly_columns[1].metric(
        "Anomaly flags", f"{anomalies.get('anomaly_count', 0):,}"
    )
    anomaly_columns[2].metric(
        "Customers affected", f"{anomalies.get('affected_customer_count', 0):,}"
    )
    st.caption(
        "Anomaly flags identify transactions for investigation; they do not "
        "establish fraud. One transaction can trigger multiple flags."
    )

    anomaly_records = anomalies.get("anomalies", [])
    if anomaly_records:
        anomaly_frame = pd.DataFrame(anomaly_records)
        if "rule" in anomaly_frame.columns:
            st.markdown("#### Anomaly flags by rule")
            rule_counts = (
                anomaly_frame.groupby("rule", dropna=False)
                .size()
                .reset_index(name="flag_count")
                .sort_values("flag_count", ascending=False)
            )
            _render_bar_chart(
                rule_counts.to_dict(orient="records"),
                x_column="rule",
                y_column="flag_count",
                empty_message="No anomaly-rule counts are available.",
            )
    _render_table(
        anomaly_records,
        "No transaction anomaly flags were returned.",
    )

    st.divider()
    st.subheader("Product Catalogue")
    product_columns = st.columns(4)
    product_columns[0].metric(
        "Products", f"{products.get('total_products', 0):,}"
    )
    price_statistics = products.get("price_statistics")
    if price_statistics:
        product_columns[1].metric(
            "Minimum listed price", _format_currency(price_statistics.get("minimum"))
        )
        product_columns[2].metric(
            "Average listed price", _format_currency(price_statistics.get("average"))
        )
        product_columns[3].metric(
            "Maximum listed price", _format_currency(price_statistics.get("maximum"))
        )
    else:
        product_columns[1].metric("Minimum listed price", "N/A")
        product_columns[2].metric("Average listed price", "N/A")
        product_columns[3].metric("Maximum listed price", "N/A")

    category_distribution = products.get("category_distribution", [])
    st.markdown("#### Products by category")
    _render_bar_chart(
        category_distribution,
        x_column="category",
        y_column="product_count",
        empty_message="No product category data is available.",
    )
    _render_table(
        category_distribution,
        "No product category data is available.",
    )
    st.caption(
        "This section describes the product catalogue. Product-level sales "
        "and revenue are not calculated because the current transaction "
        "schema does not link transactions to products."
    )

    warnings = (
        customers.get("validation_warnings", [])
        + products.get("validation_warnings", [])
    )
    if warnings:
        with st.expander("Data quality warnings"):
            for warning in warnings:
                st.warning(str(warning))
