from app.models.document import Document
from app.storage.vector_storage import VectorStorage


def test_vector_storage():

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

    storage = VectorStorage()

    result = storage.save(documents)

    assert result == 2