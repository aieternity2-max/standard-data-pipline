from app.loaders.base import BaseLoader
from app.models.document import Document
from app.config.database import get_database_engine

from sqlalchemy import text


class MySQLLoader(BaseLoader):
    """
    Loader for MySQL database tables.

    Supports:
    1. Normal loading using load()
    2. Batch loading using load_batches()
    """

    def __init__(
        self,
        database_name: str,
        table_name: str,
    ):
        if not database_name:
            raise ValueError(
                "Database name is required"
            )

        if not table_name:
            raise ValueError(
                "Table name is required"
            )

        self.database_name = database_name
        self.table_name = table_name

        self.engine = get_database_engine(
            database_name
        )

    def _create_document(
        self,
        record: dict,
        columns: list[str],
        row_number: int,
    ) -> Document:
        """
        Convert one MySQL row into a Document.
        """

        return Document(
            id=(
                f"{self.table_name}-"
                f"{row_number}"
            ),
            source=(
                f"{self.database_name}."
                f"{self.table_name}"
            ),
            source_type="mysql",
            content=str(record),
            metadata={
                "database": self.database_name,
                "table": self.table_name,
                "row_number": row_number,
                "columns": columns,
            },
        )

    def load(
        self,
        source: str | None = None,
    ) -> list[Document]:
        """
        Load all rows from the configured MySQL table.

        Suitable for small/medium-sized tables.
        """

        query = text(
            f"SELECT * FROM `{self.table_name}`"
        )

        documents = []

        with self.engine.connect() as connection:

            result = connection.execute(query)

            columns = list(result.keys())

            for row_number, row in enumerate(
                result,
                start=1,
            ):

                record = dict(
                    row._mapping
                )

                document = self._create_document(
                    record,
                    columns,
                    row_number,
                )

                documents.append(document)

        return documents

    def load_batches(
        self,
        batch_size: int = 10_000,
    ):
        """
        Load MySQL records in batches.

        Only one batch is held in memory
        at a time.
        """

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        query = text(
            f"SELECT * FROM `{self.table_name}`"
        )

        with self.engine.connect() as connection:

            result = connection.execution_options(
                stream_results=True
            ).execute(query)

            columns = list(result.keys())

            row_number = 0

            while True:

                rows = result.fetchmany(
                    batch_size
                )

                if not rows:
                    break

                documents = []

                for row in rows:

                    row_number += 1

                    record = dict(
                        row._mapping
                    )

                    document = self._create_document(
                        record,
                        columns,
                        row_number,
                    )

                    documents.append(document)

                yield documents