from pathlib import Path

from app.loaders.base import BaseLoader
from app.loaders.csv_loader import CSVLoader
from app.loaders.excel_loader import ExcelLoader
from app.loaders.json_loader import JSONLoader


class LoaderFactory:
    """
    Select the appropriate loader based on file extension.
    """

    _loaders = {
        ".csv": CSVLoader,
        ".xlsx": ExcelLoader,
        ".xls": ExcelLoader,
        ".json": JSONLoader,
        ".jsonl": JSONLoader,
    }

    @classmethod
    def get_loader(cls, source: str | Path) -> BaseLoader:
        """
        Return the appropriate loader for the source file.
        """

        file_path = Path(source)

        extension = file_path.suffix.lower()

        loader_class = cls._loaders.get(extension)

        if loader_class is None:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return loader_class()