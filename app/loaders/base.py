from abc import ABC, abstractmethod
from pathlib import Path

from app.models.document import Document


class BaseLoader(ABC):
    """
    Base interface for all data loaders.
    """

    @abstractmethod
    def load(self, source: str | Path) -> list[Document]:
        """
        Load data from a source and return Documents.
        """
        raise NotImplementedError