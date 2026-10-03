from pathlib import Path

from app.loaders.csv_loader import CSVLoader


def test_csv_loader():

    csv_file = (
        Path(__file__).parent
        / "fixtures"
        / "sample.csv"
    )

    loader = CSVLoader()

    documents = loader.load(csv_file)

    assert len(documents) == 3

    assert documents[0].source_type == "csv"

    assert documents[0].id == "sample-1"

    assert "John Smith" in documents[0].content

    assert documents[0].metadata["row_number"] == 1

    assert "customer_id" in documents[0].metadata["columns"]