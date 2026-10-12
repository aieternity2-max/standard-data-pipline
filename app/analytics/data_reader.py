"""Read structured business data from MySQL into Pandas DataFrames."""

import pandas as pd
from sqlalchemy import text

from app.config.database import get_database_engine


class StructuredDataReader:
    """Read structured tables for business analytics."""

    def __init__(self, database_name: str = "big_data_demo") -> None:
        if not database_name or not database_name.strip():
            raise ValueError("Database name must not be empty.")

        self.database_name = database_name

    def read_table(self, table_name: str) -> pd.DataFrame:
        """Read an entire table into a Pandas DataFrame."""

        allowed_tables = {"transactions", "users", "products"}

        if table_name not in allowed_tables:
            raise ValueError(
                f"Unsupported table: {table_name}. "
                f"Allowed tables: {sorted(allowed_tables)}"
            )

        engine = get_database_engine(self.database_name)

        try:
            query = text(f"SELECT * FROM `{table_name}`")

            with engine.connect() as connection:
                return pd.read_sql(query, connection)

        finally:
            engine.dispose()

    def read_transactions(self) -> pd.DataFrame:
        """Read transaction records for payment analytics."""

        return self.read_table("transactions")

    def read_users(self) -> pd.DataFrame:
        """Read customer records for customer analytics."""

        return self.read_table("users")

    def read_products(self) -> pd.DataFrame:
        """Read product records for product analytics."""

        return self.read_table("products")