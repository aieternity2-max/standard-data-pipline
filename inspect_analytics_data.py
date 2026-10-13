from sqlalchemy import text
from app.config.database import get_database_engine

engine = get_database_engine("big_data_demo")

try:
    with engine.connect() as conn:
        print("\n=== TRANSACTION SUMMARY ===")
        query = text("""
            SELECT
                COUNT(*) AS total_rows,
                MIN(transaction_date) AS first_date,
                MAX(transaction_date) AS last_date,
                SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS null_amounts,
                SUM(CASE WHEN payment_status IS NULL THEN 1 ELSE 0 END) AS null_statuses
            FROM transactions
        """)
        print(conn.execute(query).mappings().all())

        print("\n=== PAYMENT STATUS BREAKDOWN ===")
        query = text("""
            SELECT
                COALESCE(payment_status, '<NULL>') AS payment_status,
                COUNT(*) AS transaction_count,
                SUM(total_amount) AS total_amount
            FROM transactions
            GROUP BY payment_status
            ORDER BY transaction_count DESC
        """)
        print(conn.execute(query).mappings().all())

        print("\n=== CUSTOMERS BY COUNTRY ===")
        query = text("""
            SELECT
                COALESCE(country, '<NULL>') AS country,
                COUNT(*) AS customer_count
            FROM users
            GROUP BY country
            ORDER BY customer_count DESC
        """)
        print(conn.execute(query).mappings().all())

        print("\n=== TABLE COUNTS ===")
        query = text("""
            SELECT
                (SELECT COUNT(*) FROM users) AS users_count,
                (SELECT COUNT(*) FROM products) AS products_count,
                (SELECT COUNT(*) FROM transactions) AS transactions_count
        """)
        print(conn.execute(query).mappings().all())

finally:
    engine.dispose()
