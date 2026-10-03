import json
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.loaders.base import BaseLoader
from app.models.document import Document


class CSVLoader(BaseLoader):
    """
    Load CSV files and convert each row into a Document.
    """

    def load(self, source: str | Path) -> list[Document]:
        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        try:
            dataframe = pd.read_csv(file_path)

        except EmptyDataError as exc:
            raise ValueError(
                f"CSV file is empty: {file_path}"
            ) from exc

        except ParserError as exc:
            raise ValueError(
                f"Unable to parse CSV file: {file_path}"
            ) from exc

        documents: list[Document] = []

        for row_number, (_, row) in enumerate(
            dataframe.iterrows(),
            start=1,
        ):
            row_data = row.to_dict()

            content = json.dumps(
                row_data,
                default=str,
            )

            document = Document(
                id=f"{file_path.stem}-{row_number}",
                source=str(file_path),
                source_type="csv",
                content=content,
                metadata={
                    "row_number": row_number,
                    "columns": list(dataframe.columns),
                },
            )

            documents.append(document)

        return documents