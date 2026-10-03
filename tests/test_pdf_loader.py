from pathlib import Path

import pytest

from app.loaders.pdf_loader import PDFLoader


def test_pdf_loader():

    pdf_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.pdf"
    )

    loader = PDFLoader()

    documents = loader.load(pdf_file)

    assert len(documents) > 0

    assert documents[0].source_type == "pdf"

    assert documents[0].metadata["page_number"] == 1

    assert documents[0].metadata["total_pages"] >= 1


def test_pdf_loader_batches():

    pdf_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.pdf"
    )

    loader = PDFLoader()

    batches = list(
        loader.load_batches(
            pdf_file,
            batch_size=1,
        )
    )

    assert len(batches) > 0

    assert len(batches[0]) == 1

    assert batches[0][0].source_type == "pdf"


def test_pdf_loader_invalid_batch_size():

    pdf_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.pdf"
    )

    loader = PDFLoader()

    with pytest.raises(ValueError):

        list(
            loader.load_batches(
                pdf_file,
                batch_size=0,
            )
        )