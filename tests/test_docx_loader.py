from pathlib import Path

import pytest

from app.loaders.docx_loader import DOCXLoader


def test_docx_loader():

    docx_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.docx"
    )

    loader = DOCXLoader()

    documents = loader.load(docx_file)

    assert len(documents) > 0

    assert documents[0].source_type == "docx"

    assert (
        documents[0].metadata["paragraph_number"]
        == 1
    )


def test_docx_loader_batches():

    docx_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.docx"
    )

    loader = DOCXLoader()

    batches = list(
        loader.load_batches(
            docx_file,
            batch_size=2,
        )
    )

    assert len(batches) > 0

    assert len(batches[0]) <= 2

    assert batches[0][0].source_type == "docx"


def test_docx_loader_invalid_batch_size():

    docx_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.docx"
    )

    loader = DOCXLoader()

    with pytest.raises(ValueError):

        list(
            loader.load_batches(
                docx_file,
                batch_size=0,
            )
        )