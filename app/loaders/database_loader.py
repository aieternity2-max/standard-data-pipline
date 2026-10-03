import sqlite3
from pathlib import Path

from app.loaders.base import BaseLoader
from app.models.document import Document


class DatabaseLoader(BaseLoader):
    """
    Loader for SQLite databases.

    Supports:
    1. Normal loading using load()
    2. Batch loading using load_batches()
    """

    def load(
        self,
        source: str | Path,
        table: str
    ) -> list[Document]:
        """
        Load all records from a SQLite table.

        Suitable for small/medium-sized tables.
        """

        database_path = Path(source)

        if not database_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {database_path}"
            )

        if not database_path.is_file():
            raise ValueError(
                f"Source is not a file: {database_path}"
            )

        if not table:
            raise ValueError(
                "Table name must be provided"
            )

        connection = sqlite3.connect(database_path)

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"SELECT * FROM {table}"
            )

            columns = [
                description[0]
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            documents = []

            for row_number, row in enumerate(
                rows,
                start=1
            ):

                record = dict(
                    zip(columns, row)
                )

                document = Document(
                    id=f"{table}-{row_number}",
                    source=str(database_path),
                    source_type="database",
                    content=str(record),
                    metadata={
                        "row_number": row_number,
                        "columns": columns,
                        "table": table
                    }
                )

                documents.append(document)

            return documents

        finally:
            connection.close()

    def load_batches(
        self,
        source: str | Path,
        table: str,
        batch_size: int = 10_000
    ):
        """
        Load database records in batches.

        Only one batch is held in memory at a time.
        """

        database_path = Path(source)

        if not database_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {database_path}"
            )

        if not database_path.is_file():
            raise ValueError(
                f"Source is not a file: {database_path}"
            )

        if not table:
            raise ValueError(
                "Table name must be provided"
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        connection = sqlite3.connect(database_path)

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"SELECT * FROM {table}"
            )

            columns = [
                description[0]
                for description in cursor.description
            ]

            row_number = 0

            while True:

                rows = cursor.fetchmany(batch_size)

                if not rows:
                    break

                documents = []

                for row in rows:

                    row_number += 1

                    record = dict(
                        zip(columns, row)
                    )

                    document = Document(
                        id=f"{table}-{row_number}",
                        source=str(database_path),
                        source_type="database",
                        content=str(record),
                        metadata={
                            "row_number": row_number,
                            "columns": columns,
                            "table": table
                        }
                    )

                    documents.append(document)

                yield documents

        finally:
            connection.close()