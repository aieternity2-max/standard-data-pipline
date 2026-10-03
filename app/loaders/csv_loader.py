import json
from pathlib import Path

import pandas as pd

from pandas.errors import EmptyDataError, ParserError
from app.loaders.base import BaseLoader
from app.models.document import Document





class CSVLoader(BaseLoader):
    """
    Loader for CSV files.

    Supports:
    1. Normal loading using load()
    2. Batch loading using load_batches()
    """

    def load(self, source: str | Path) -> list[Document]:
        """
        Load the complete CSV file into memory.

        Suitable for small and medium-sized files.
        """

        file_path = Path(source)

        # Check whether the file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        # Read CSV file
        dataframe = pd.read_csv(file_path)

        # Store column names
        columns = list(dataframe.columns)

        documents = []

        # Convert each row into a Document
        for index, row in dataframe.iterrows():

            document = Document(
                id=f"{file_path.stem}-{index + 1}",
                source=str(file_path),
                source_type="csv",
                content=str(row.to_dict()),
                metadata={
                    "row_number": index + 1,
                    "columns": columns
                }
            )

            documents.append(document)

        return documents

    def load_batches(
        self,
        source: str | Path,
        batch_size: int = 100_000
    ):
        """
        Load a CSV file in batches.

        This prevents the complete CSV file from
        being loaded into memory at once.

        Example:
            batch_size=100000

        means approximately 100,000 rows are
        processed at a time.
        """

        file_path = Path(source)

        # Check whether the file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        # Validate batch size
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        # Read CSV in chunks
        for dataframe in pd.read_csv(
            file_path,
            chunksize=batch_size
        ):

            # Get column names
            columns = list(dataframe.columns)

            documents = []

            # Convert each row in the batch into a Document
            for index, row in dataframe.iterrows():

                document = Document(
                    id=f"{file_path.stem}-{index + 1}",
                    source=str(file_path),
                    source_type="csv",
                    content=str(row.to_dict()),
                    metadata={
                        "row_number": index + 1,
                        "columns": columns
                    }
                )

                documents.append(document)

            # Return one batch at a time
            yield documents