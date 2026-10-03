import sqlite3
from pathlib import Path

from app.loaders.database_loader import DatabaseLoader


def create_test_database(database_path: Path):

    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER,
            name TEXT,
            email TEXT,
            age INTEGER
        )
        """
    )

    customers = [
        (101, "Alice", "alice@example.com", 31),
        (102, "Bob", "bob@example.com", 27),
        (103, "Charlie", "charlie@example.com", 45),
        (104, "David", "david@example.com", 36),
        (105, "Emma", "emma@example.com", 29),
    ]

    cursor.executemany(
        """
        INSERT INTO customers
        VALUES (?, ?, ?, ?)
        """,
        customers
    )

    connection.commit()
    connection.close()


def test_database_loader(tmp_path):

    database_file = tmp_path / "sample.db"

    create_test_database(database_file)

    loader = DatabaseLoader()

    documents = loader.load(
        database_file,
        "customers"
    )

    assert len(documents) == 5

    assert documents[0].id == "customers-1"

    assert documents[0].source_type == "database"

    assert documents[0].metadata["table"] == "customers"

    assert documents[0].metadata["row_number"] == 1

    assert "customer_id" in (
        documents[0].metadata["columns"]
    )


def test_database_loader_batches(tmp_path):

    database_file = tmp_path / "sample.db"

    create_test_database(database_file)

    loader = DatabaseLoader()

    batches = list(
        loader.load_batches(
            database_file,
            "customers",
            batch_size=2
        )
    )

    assert len(batches) == 3

    assert len(batches[0]) == 2

    assert len(batches[1]) == 2

    assert len(batches[2]) == 1

    assert batches[0][0].id == "customers-1"

    assert batches[1][0].id == "customers-3"

    assert batches[2][0].id == "customers-5"