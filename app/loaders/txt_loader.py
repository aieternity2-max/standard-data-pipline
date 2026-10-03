from pathlib import Path

from app.loaders.base import BaseLoader
from app.models.document import Document


class TXTLoader(BaseLoader):
    """
    Loader for plain text files.

    Supports:
    1. Normal loading using load()
    2. Batch loading using load_batches()
    """

    def load(self, source: str | Path) -> list[Document]:
        """
        Load a complete text file into a Document.
        """

        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"TXT file not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        if file_path.suffix.lower() != ".txt":
            raise ValueError(
                f"Unsupported TXT file type: {file_path.suffix}"
            )

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError as exc:
            raise ValueError(
                f"Unable to decode TXT file as UTF-8: {file_path}"
            ) from exc

        document = Document(
            id=f"{file_path.stem}-1",
            source=str(file_path),
            source_type="txt",
            content=content,
            metadata={
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
            },
        )

        return [document]

    def load_batches(
        self,
        source: str | Path,
        chunk_size: int = 100_000,
    ):
        """
        Load a large text file in chunks.

        Each chunk becomes a separate Document.
        """

        file_path = Path(source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"TXT file not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0"
            )

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:

                chunk_number = 1

                while True:

                    content = file.read(chunk_size)

                    if not content:
                        break

                    document = Document(
                        id=f"{file_path.stem}-{chunk_number}",
                        source=str(file_path),
                        source_type="txt",
                        content=content,
                        metadata={
                            "chunk_number": chunk_number,
                            "file_name": file_path.name,
                            "file_size": file_path.stat().st_size,
                        },
                    )

                    yield [document]

                    chunk_number += 1

        except UnicodeDecodeError as exc:

            raise ValueError(
                f"Unable to decode TXT file as UTF-8: {file_path}"
            ) from exc