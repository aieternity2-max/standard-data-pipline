from pathlib import Path

from app.loaders.excel_loader import ExcelLoader


def test_excel_loader_batches():

    excel_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.xlsx"
    )

    loader = ExcelLoader()

    batches = list(
        loader.load_batches(
            excel_file,
            batch_size=2
        )
    )

    assert len(batches) > 0

    assert len(batches[0]) <= 2

    assert batches[0][0].source_type == "excel"

    assert batches[0][0].metadata["sheet_name"] is not None