"""Product catalogue analytics."""

from typing import Any

import pandas as pd

from app.analytics.data_reader import StructuredDataReader


class ProductAnalytics:
    """Analyze product catalogue size, category distribution, and pricing."""

    REQUIRED_COLUMNS = {
        "product_id",
        "product_name",
        "category",
        "price",
    }

    def __init__(
        self,
        data_reader: StructuredDataReader | None = None,
    ) -> None:
        self.data_reader = data_reader or StructuredDataReader()

    def analyze(
        self,
        dataframe: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """Validate and analyze a product catalogue DataFrame."""

        if dataframe is None:
            dataframe = self.data_reader.read_products()

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Product input must be a Pandas DataFrame.")

        missing_columns = self.REQUIRED_COLUMNS.difference(dataframe.columns)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Missing required product columns: {missing}"
            )

        # Work on a copy so the caller's DataFrame remains unchanged.
        products = dataframe.copy(deep=True)

        if products.empty:
            return {
                "total_products": 0,
                "catalogue_empty": True,
                "category_distribution": [],
                "price_statistics": None,
                "validation_warnings": [
                    "Product catalogue is empty."
                ],
            }

        # Product IDs must exist and be unique.
        if products["product_id"].isna().any():
            raise ValueError("Product IDs must not be missing.")

        if products["product_id"].duplicated().any():
            raise ValueError("Duplicate product IDs were found.")

        # Product names must be present and nonblank.
        product_names = products["product_name"].astype("string").str.strip()

        if (product_names.isna() | product_names.eq("")).any():
            raise ValueError("Product names must not be missing.")

        products["product_name"] = product_names

        # Prices must be numeric, present, and nonnegative.
        prices = pd.to_numeric(products["price"], errors="coerce")

        if prices.isna().any():
            raise ValueError(
                "Product prices must be present and numeric."
            )

        if (prices < 0).any():
            raise ValueError("Product prices must not be negative.")

        products["price"] = prices

        # Normalize missing or blank categories without changing the source.
        categories = products["category"].astype("string").str.strip()
        missing_categories = categories.isna() | categories.eq("")

        validation_warnings = []

        if missing_categories.any():
            validation_warnings.append(
                "One or more products have no category recorded; "
                "they are grouped as Unknown."
            )

        products["category"] = categories.mask(
            missing_categories,
            "Unknown",
        )

        total_products = len(products)

        category_counts = (
            products.groupby("category", dropna=False)
            .size()
            .sort_index()
        )

        category_distribution = [
            {
                "category": str(category),
                "product_count": int(count),
                "product_share_pct": round(
                    int(count) / total_products * 100,
                    2,
                ),
            }
            for category, count in category_counts.items()
        ]

        price_statistics = {
            "minimum": round(float(products["price"].min()), 2),
            "maximum": round(float(products["price"].max()), 2),
            "average": round(float(products["price"].mean()), 2),
        }

        return {
            "total_products": total_products,
            "catalogue_empty": False,
            "category_distribution": category_distribution,
            "price_statistics": price_statistics,
            "validation_warnings": validation_warnings,
        }
