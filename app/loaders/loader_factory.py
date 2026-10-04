from pathlib import Path

from app.loaders.base import BaseLoader
from app.loaders.csv_loader import CSVLoader
from app.loaders.excel_loader import ExcelLoader
from app.loaders.json_loader import JSONLoader
from app.loaders.api_loader import APILoader
from app.loaders.pdf_loader import PDFLoader
from app.loaders.docx_loader import DOCXLoader


class LoaderFactory:
    """
    Select the appropriate loader based on source type.
    """

    _loaders = {
        ".csv": CSVLoader,
        ".xlsx": ExcelLoader,
        ".xls": ExcelLoader,
        ".json": JSONLoader,
        ".jsonl": JSONLoader,
        ".pdf": PDFLoader,
        ".docx": DOCXLoader,
    }

    @classmethod
    def get_loader(cls, source: str | Path) -> BaseLoader:
        """
        Return the appropriate loader for a file source.
        """

        file_path = Path(source)

        extension = file_path.suffix.lower()

        loader_class = cls._loaders.get(extension)

        if loader_class is None:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return loader_class()

    @classmethod
    def get_api_loader(cls) -> APILoader:
        """
        Return the API loader.
        """

        return APILoader()
    