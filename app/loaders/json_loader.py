import json
from pathlib import Path

from app.loaders.base import BaseLoader
from app.models.document import Document


class JSONLoader(BaseLoader):
    """
    Loader for JSON files.

    Supports a JSON array containing records.
    Each record is converted into a standard Document.
    """

    def load(self, source: str | Path) -> list[Document]:
        file_path = Path(source)

        # 1. Check that the file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"JSON file not found: {file_path}"
            )

        # 2. Check that the path is a file
        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        # 3. Check extension
        if file_path.suffix.lower() != ".json":
            raise ValueError(
                f"Unsupported JSON file type: {file_path.suffix}"
            )

        # 4. Read JSON
        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON file: {file_path}"
            ) from exc

        # 5. JSON must contain a list of records
        if not isinstance(data, list):
            raise ValueError(
                "JSON root must be a list of records"
            )

        documents: list[Document] = []

        # 6. Convert each record into a Document
        for row_number, record in enumerate(
            data,
            start=1,
        ):

            if not isinstance(record, dict):
                raise ValueError(
                    f"JSON record {row_number} must be an object"
                )

            document = Document(
                id=f"{file_path.stem}-{row_number}",
                source=str(file_path),
                source_type="json",
                content=json.dumps(
                    record,
                    ensure_ascii=False,
                ),
                metadata={
                    "row_number": row_number,
                    "columns": list(record.keys()),
                },
            )

            documents.append(document)

        return documents