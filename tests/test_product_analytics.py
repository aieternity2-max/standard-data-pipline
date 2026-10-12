"""Tests for product catalogue analytics."""

import pandas as pd
import pytest

from app.analytics.product_analytics import ProductAnalytics


@pytest.fixture
def sample_products():
    return pd.DataFrame(
        {
            "product_id": [1, 2, 3, 4, 5],
            "product_name": [
                "Laptop",
                "Mouse",
                "Keyboard",
                "Monitor",
                "Webcam",
            ],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
                "Electronics",
                "Accessories",
            ],
            "price": [1200.00, 25.00, 45.00, 300.00, 60.00],
        }
    )


def test_product_count(sample_products):
    result = ProductAnalytics().analyze(sample_products)

    assert result["total_products"] == 5
    assert result["catalogue_empty"] is False


def test_category_distribution(sample_products):
    result = ProductAnalytics().analyze(sample_products)

    distribution = {
        item["category"]: item
        for item in result["category_distribution"]
    }

    assert distribution["Electronics"]["product_count"] == 2
    assert distribution["Accessories"]["product_count"] == 3


def test_category_shares(sample_products):
    result = ProductAnalytics().analyze(sample_products)

    distribution = {
        item["category"]: item
        for item in result["category_distribution"]
    }

    assert distribution["Electronics"]["product_share_pct"] == 40.0
    assert distribution["Accessories"]["product_share_pct"] == 60.0


def test_price_statistics(sample_products):
    result = ProductAnalytics().analyze(sample_products)

    assert result["price_statistics"] == {
        "minimum": 25.00,
        "maximum": 1200.00,
        "average": 326.00,
    }


def test_missing_category_is_reported_as_unknown(sample_products):
    products = sample_products.copy()
    products.loc[0, "category"] = None

    result = ProductAnalytics().analyze(products)

    distribution = {
        item["category"]: item
        for item in result["category_distribution"]
    }

    assert distribution["Unknown"]["product_count"] == 1
    assert any(
        "category" in warning.lower()
        for warning in result["validation_warnings"]
    )


def test_empty_catalogue_is_reported():
    products = pd.DataFrame(
        columns=["product_id", "product_name", "category", "price"]
    )

    result = ProductAnalytics().analyze(products)

    assert result["total_products"] == 0
    assert result["catalogue_empty"] is True
    assert result["category_distribution"] == []
    assert result["price_statistics"] is None


def test_duplicate_product_ids_are_rejected(sample_products):
    products = pd.concat(
        [sample_products, sample_products.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="Duplicate product IDs"):
        ProductAnalytics().analyze(products)


def test_missing_product_id_is_rejected(sample_products):
    products = sample_products.copy()
    products.loc[0, "product_id"] = None

    with pytest.raises(ValueError, match="Product IDs must not be missing"):
        ProductAnalytics().analyze(products)


def test_missing_product_name_is_rejected(sample_products):
    products = sample_products.copy()
    products.loc[0, "product_name"] = None

    with pytest.raises(ValueError, match="Product names must not be missing"):
        ProductAnalytics().analyze(products)


@pytest.mark.parametrize("invalid_price", [-1.0, None, "invalid"])
def test_invalid_prices_are_rejected(sample_products, invalid_price):
    products = sample_products.astype({"price": "object"}).copy()
    products.loc[0, "price"] = invalid_price

    with pytest.raises(ValueError, match="Product prices"):
        ProductAnalytics().analyze(products)


def test_negative_price_is_rejected(sample_products):
    products = sample_products.copy()
    products.loc[0, "price"] = -10.00

    with pytest.raises(ValueError, match="must not be negative"):
        ProductAnalytics().analyze(products)


def test_missing_required_column_is_rejected(sample_products):
    products = sample_products.drop(columns=["price"])

    with pytest.raises(ValueError, match="Missing required product columns"):
        ProductAnalytics().analyze(products)


def test_non_dataframe_input_is_rejected():
    with pytest.raises(ValueError, match="Pandas DataFrame"):
        ProductAnalytics().analyze([{"product_id": 1}])


def test_input_dataframe_is_not_modified(sample_products):
    original = sample_products.copy(deep=True)

    ProductAnalytics().analyze(sample_products)

    pd.testing.assert_frame_equal(sample_products, original)
