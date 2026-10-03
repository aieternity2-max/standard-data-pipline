from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Common internal representation for all ingested data.
    """

    id: str

    source: str

    source_type: str

    content: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )