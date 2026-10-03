from app.loaders.csv_loader import CSVLoader
from app.loaders.excel_loader import ExcelLoader
from app.loaders.loader_factory import LoaderFactory
from app.loaders.json_loader import JSONLoader


def test_csv_loader_factory():

    loader = LoaderFactory.get_loader(
        "sample.csv"
    )

    assert isinstance(loader, CSVLoader)


def test_excel_loader_factory():

    loader = LoaderFactory.get_loader(
        "sample.xlsx"
    )

    assert isinstance(loader, ExcelLoader)

def test_json_loader_factory():

    loader = LoaderFactory.get_loader(
        "sample.json"
    )

    assert isinstance(loader, JSONLoader)


def test_unsupported_file_type():

    try:
        LoaderFactory.get_loader("sample.pdf")
        assert False
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)