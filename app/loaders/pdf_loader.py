from pathlib import Path

from pypdf import PdfReader

from app.loaders.base import BaseLoader
from app.models.document import Document


class PDFLoader(BaseLoader):
    """
    Loader for PDF files.

    Supports:
    1. Normal page-by-page loading using load()
    2. Batch loading using load_batches()
    """

    def load(self, source: str | Path) -> list[Document]:
        """
        Load every PDF page as a separate Document.
        """

        file_path = Path(source)

        self._validate_file(file_path)

        try:
            reader = PdfReader(str(file_path))

        except Exception as exc:
            raise ValueError(
                f"Unable to read PDF file: {file_path}"
            ) from exc

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            content = page.extract_text() or ""

            document = Document(
                id=f"{file_path.stem}-{page_number}",
                source=str(file_path),
                source_type="pdf",
                content=content,
                metadata={
                    "file_name": file_path.name,
                    "page_number": page_number,
                    "total_pages": len(reader.pages),
                },
            )

            documents.append(document)

        return documents

    def load_batches(
        self,
        source: str | Path,
        batch_size: int = 10,
    ):
        """
        Load PDF pages in batches.

        Example:

        25-page PDF + batch_size=10

        Batch 1 → pages 1-10
        Batch 2 → pages 11-20
        Batch 3 → pages 21-25
        """

        file_path = Path(source)

        self._validate_file(file_path)

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0"
            )

        try:
            reader = PdfReader(str(file_path))

        except Exception as exc:
            raise ValueError(
                f"Unable to read PDF file: {file_path}"
            ) from exc

        total_pages = len(reader.pages)

        batch = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            content = page.extract_text() or ""

            document = Document(
                id=f"{file_path.stem}-{page_number}",
                source=str(file_path),
                source_type="pdf",
                content=content,
                metadata={
                    "file_name": file_path.name,
                    "page_number": page_number,
                    "total_pages": total_pages,
                },
            )

            batch.append(document)

            if len(batch) == batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

    @staticmethod
    def _validate_file(file_path: Path) -> None:
        """
        Validate PDF input.
        """

        if not file_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Source is not a file: {file_path}"
            )

        if file_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Unsupported PDF file type: {file_path.suffix}"
            )