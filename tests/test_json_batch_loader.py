from pathlib import Path

from app.loaders.json_loader import JSONLoader


def test_json_loader_batches():

    jsonl_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.jsonl"
    )

    loader = JSONLoader()

    batches = list(
        loader.load_batches(
            jsonl_file,
            batch_size=2
        )
    )

    # 5 records with batch size 2
    # should produce 3 batches
    assert len(batches) == 3

    # First batch
    assert len(batches[0]) == 2

    # Second batch
    assert len(batches[1]) == 2

    # Third batch
    assert len(batches[2]) == 1

    # Check Document structure
    assert batches[0][0].source_type == "jsonl"

    assert batches[0][0].id == "sample-1"

    assert batches[0][0].metadata["row_number"] == 1

    assert "customer_id" in batches[0][0].metadata["columns"]