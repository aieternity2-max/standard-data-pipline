from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from app.loaders.base import BaseLoader
from app.models.document import Document


class ExcelLoader(BaseLoader):
    """
    Loader for Excel files.

    Reads .xlsx files and converts each row into
    a standard Document object.
    """

    def load(self, source: str | Path) -> list[Document]:
        file_path = Path(source)

        # 1. Check that the file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"Excel file not found: {file_path}"
            )

        # 2. Check that the path is actually a file
        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        # 3. Check file extension
        if file_path.suffix.lower() not in {".xlsx", ".xls"}:
            raise ValueError(
                f"Unsupported Excel file type: {file_path.suffix}"
            )

        # 4. Read Excel file
        try:
            dataframe = pd.read_excel(
                file_path,
                engine="openpyxl",
            )

        except EmptyDataError as exc:
            raise ValueError(
                f"Excel file is empty: {file_path}"
            ) from exc

        # 5. Convert rows into Documents
        documents: list[Document] = []

        for row_number, (_, row) in enumerate(
            dataframe.iterrows(),
            start=1,
        ):
            row_data = row.to_dict()

            document = Document(
                id=f"{file_path.stem}-{row_number}",
                source=str(file_path),
                source_type="excel",
                content=str(row_data),
                metadata={
                    "row_number": row_number,
                    "columns": list(dataframe.columns),
                },
            )

            documents.append(document)

        return documents