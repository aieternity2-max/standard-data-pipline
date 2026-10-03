from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from openpyxl import load_workbook

from app.loaders.base import BaseLoader
from app.models.document import Document


class ExcelLoader(BaseLoader):
    """
    Loader for Excel files.

    Supports:
    1. Normal loading using load()
    2. Batch loading using load_batches()
    """

    def load(self, source: str | Path) -> list[Document]:
        """
        Load the complete Excel file into memory.

        Suitable for small and medium-sized Excel files.
        """

        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Excel file not found: {file_path}"
            )

        dataframe = pd.read_excel(
            file_path,
            engine="openpyxl"
        )

        columns = list(dataframe.columns)

        documents = []

        for index, row in dataframe.iterrows():

            document = Document(
                id=f"{file_path.stem}-{index + 1}",
                source=str(file_path),
                source_type="excel",
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
        Load an Excel file in batches.

        Uses openpyxl read-only mode so that the
        entire workbook does not need to be loaded
        into memory.
        """

        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Excel file not found: {file_path}"
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        workbook = load_workbook(
            filename=file_path,
            read_only=True,
            data_only=True
        )

        try:

            for worksheet in workbook.worksheets:

                rows = worksheet.iter_rows(
                    values_only=True
                )

                # First row is treated as the header
                headers = next(rows, None)

                if headers is None:
                    continue

                headers = [
                    str(column)
                    if column is not None
                    else f"column_{index + 1}"
                    for index, column in enumerate(headers)
                ]

                documents = []

                row_number = 1

                for row in rows:

                    row_number += 1

                    row_data = dict(
                        zip(headers, row)
                    )

                    document = Document(
                        id=f"{file_path.stem}-{row_number - 1}",
                        source=str(file_path),
                        source_type="excel",
                        content=str(row_data),
                        metadata={
                            "row_number": row_number - 1,
                            "columns": headers,
                            "sheet_name": worksheet.title
                        }
                    )

                    documents.append(document)

                    # Return one batch when batch_size is reached
                    if len(documents) >= batch_size:
                        yield documents
                        documents = []

                # Return remaining records
                if documents:
                    yield documents

        finally:
            workbook.close()