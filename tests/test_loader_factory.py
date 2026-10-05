from app.loaders.csv_loader import CSVLoader
from app.loaders.excel_loader import ExcelLoader
from app.loaders.loader_factory import LoaderFactory
from app.loaders.json_loader import JSONLoader
from app.loaders.mysql_loader import MySQLLoader
import pytest

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

def test_jsonl_loader_factory():

    loader = LoaderFactory.get_loader(
        "sample.jsonl"
    )

    assert isinstance(loader, JSONLoader)

def test_unsupported_file_type():

    try:
        LoaderFactory.get_loader("sample.pdf")
        assert False
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)


def test_unsupported_file_type():

    with pytest.raises(ValueError):

        LoaderFactory.get_loader(
            "sample.xyz"
        )

def test_mysql_loader_factory():

    loader = LoaderFactory.get_mysql_loader(
        database_name="OFFICE",
        table_name="employee",
    )

    assert isinstance(
        loader,
        MySQLLoader,
    )

    assert loader.database_name == "OFFICE"

    assert loader.table_name == "employee"