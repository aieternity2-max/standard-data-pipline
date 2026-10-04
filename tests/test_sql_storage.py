from app.models.document import Document
from app.storage.sql_storage import SQLStorage


def test_sql_storage():

    documents = [
        Document(
            id="doc-1",
            source="sample.txt",
            source_type="txt",
            content="Hello",
            metadata={},
        ),
        Document(
            id="doc-2",
            source="sample.txt",
            source_type="txt",
            content="World",
            metadata={},
        ),
    ]

    storage = SQLStorage()

    result = storage.save(documents)

    assert result == 2