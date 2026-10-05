
import os
from app.models.document import Document
from app.config.settings import settings



from app.config.database import (
    get_database_engine,
)


class SQLStorage:
    """
    Storage interface for SQL databases.

    Connects to a configured SQL database.

    Actual table mapping and persistence
    will be implemented later.
    """

    def __init__(
        self,
        database_name: str | None = None,
    ):
        """
        Initialize SQL storage.

        If database_name is not provided,
        MYSQL_DATABASE from .env is used.
        """

        if database_name is None:

         database_name = settings.mysql_database

        if not database_name:

            raise ValueError(
                "Database name is required"
            )

        self.database_name = database_name

        self.engine = get_database_engine(
            database_name
        )

    def test_connection(self) -> bool:
        """
        Test the SQL database connection.
        """

        try:

            with self.engine.connect():

                return True

        except Exception:

            return False

    def save(
        self,
        documents: list[Document],
    ) -> int:
        """
        Validate documents for SQL storage.

        Actual database insertion will be
        implemented after the target table
        schema is finalized.

        Returns the number of documents
        processed.
        """

        if not isinstance(
            documents,
            list,
        ):
            raise TypeError(
                "documents must be a list"
            )

        for document in documents:

            if not isinstance(
                document,
                Document,
            ):
                raise TypeError(
                    "All items must be Document instances"
                )

        return len(documents)