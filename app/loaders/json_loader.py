import json
from pathlib import Path

from app.loaders.base import BaseLoader
from app.models.document import Document


class JSONLoader(BaseLoader):
    """
    Loader for JSON and JSON Lines files.

    Supports:
    1. Normal JSON loading using load()
    2. Batch JSON Lines loading using load_batches()
    """

    def load(self, source: str | Path) -> list[Document]:
        """
        Load a standard JSON file.

        The JSON root must be a list of objects.

        Example:

        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        """

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
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON file: {file_path}"
            ) from exc

        # 5. JSON root must be a list
        if not isinstance(data, list):
            raise ValueError(
                "JSON root must be a list of records"
            )

        documents: list[Document] = []

        # 6. Convert records into Documents
        for row_number, record in enumerate(
            data,
            start=1
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
                    ensure_ascii=False
                ),
                metadata={
                    "row_number": row_number,
                    "columns": list(record.keys())
                }
            )

            documents.append(document)

        return documents

    def load_batches(
        self,
        source: str | Path,
        batch_size: int = 10_000
    ):
        """
        Load a JSON Lines (.jsonl) file in batches.

        JSON Lines format:

        {"id": 1, "name": "Alice"}
        {"id": 2, "name": "Bob"}
        {"id": 3, "name": "Charlie"}

        Each line represents one JSON object.

        This allows large JSON datasets to be processed
        without loading the entire file into memory.
        """

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
        if file_path.suffix.lower() != ".jsonl":
            raise ValueError(
                "Batch loading requires a .jsonl file"
            )

        # 4. Validate batch size
        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        documents = []
        row_number = 0

        # 5. Stream the file line by line
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1
            ):

                # Skip empty lines
                line = line.strip()

                if not line:
                    continue

                # Parse JSON object
                try:
                    record = json.loads(line)

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {line_number}"
                    ) from exc

                # Each JSONL line must be an object
                if not isinstance(record, dict):
                    raise ValueError(
                        f"JSONL record on line "
                        f"{line_number} must be an object"
                    )

                row_number += 1

                document = Document(
                    id=f"{file_path.stem}-{row_number}",
                    source=str(file_path),
                    source_type="jsonl",
                    content=json.dumps(
                        record,
                        ensure_ascii=False
                    ),
                    metadata={
                        "row_number": row_number,
                        "columns": list(record.keys())
                    }
                )

                documents.append(document)

                # Return batch when batch size is reached
                if len(documents) >= batch_size:
                    yield documents
                    documents = []

        # 6. Return remaining records
        if documents:
            yield documents