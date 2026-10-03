from pathlib import Path

import pytest

from app.loaders.excel_loader import ExcelLoader


def test_excel_loader():

    excel_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.xlsx"
    )

    loader = ExcelLoader()

    documents = loader.load(excel_file)

    assert len(documents) == 20

    assert documents[0].source_type == "excel"

    assert documents[0].id == "sample-1"

    assert "Alice" in documents[0].content

    assert documents[0].metadata["row_number"] == 1

    assert "customer_id" in documents[0].metadata["columns"]


def test_excel_loader_missing_file():

    loader = ExcelLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("does-not-exist.xlsx")