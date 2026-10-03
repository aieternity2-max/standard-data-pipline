from pathlib import Path

import pytest

from app.loaders.txt_loader import TXTLoader


def test_txt_loader():

    txt_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.txt"
    )

    loader = TXTLoader()

    documents = loader.load(txt_file)

    assert len(documents) == 1

    assert documents[0].id == "sample-1"

    assert documents[0].source_type == "txt"

    assert "Alice" in documents[0].content

    assert documents[0].metadata["file_name"] == "sample.txt"


def test_txt_loader_batches():

    txt_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.txt"
    )

    loader = TXTLoader()

    batches = list(
        loader.load_batches(
            txt_file,
            chunk_size=30,
        )
    )

    assert len(batches) > 1

    assert batches[0][0].source_type == "txt"

    assert batches[0][0].metadata["chunk_number"] == 1


def test_txt_loader_invalid_chunk_size():

    txt_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.txt"
    )

    loader = TXTLoader()

    with pytest.raises(ValueError):

        list(
            loader.load_batches(
                txt_file,
                chunk_size=0,
            )
        )