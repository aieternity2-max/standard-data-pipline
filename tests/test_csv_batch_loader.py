from pathlib import Path

from app.loaders.csv_loader import CSVLoader


def test_csv_loader_batches():

    csv_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.csv"
    )

    loader = CSVLoader()

    batches = list(
        loader.load_batches(
            csv_file,
            batch_size=2
        )
    )

    assert len(batches) > 0

    total_documents = sum(
        len(batch)
        for batch in batches
    )

    assert total_documents > 0