from pathlib import Path

import pytest

from app.loaders.json_loader import JSONLoader


def test_json_loader():

    json_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.json"
    )

    loader = JSONLoader()

    documents = loader.load(json_file)

    assert len(documents) == 10

    assert documents[0].source_type == "json"

    assert documents[0].id == "sample-1"

    assert "Alice" in documents[0].content

    assert documents[0].metadata["row_number"] == 1

    assert "customer_id" in documents[0].metadata["columns"]


def test_json_loader_missing_file():

    loader = JSONLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("does-not-exist.json")


def test_json_loader_invalid_root():

    json_file = (
        Path(__file__).parent
        / "fixtures"
        / "invalid_root.json"
    )

    json_file.write_text(
        '{"customer_id": 101}',
        encoding="utf-8",
    )

    loader = JSONLoader()

    with pytest.raises(ValueError, match="root must be a list"):
        loader.load(json_file)

    json_file.unlink()