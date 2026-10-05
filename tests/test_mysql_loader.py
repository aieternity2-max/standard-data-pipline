from app.loaders.mysql_loader import MySQLLoader


def test_mysql_loader():

    loader = MySQLLoader(
        database_name="OFFICE",
        table_name="employee",
    )

    documents = loader.load()

    assert len(documents) > 0

    assert documents[0].source == (
        "OFFICE.employee"
    )

    assert documents[0].source_type == "mysql"

    assert documents[0].metadata["database"] == (
        "OFFICE"
    )

    assert documents[0].metadata["table"] == (
        "employee"
    )

    assert (
        documents[0].metadata["row_number"]
        == 1
    )

    assert "EMPID" in (
        documents[0].metadata["columns"]
    )

    assert "EMP_NAME" in (
        documents[0].metadata["columns"]
    )

def test_mysql_loader_batches():

    loader = MySQLLoader(
        database_name="OFFICE",
        table_name="employee",
    )

    batches = list(
        loader.load_batches(
            batch_size=2
        )
    )

    assert len(batches) > 0

    assert len(batches[0]) == 2

    assert batches[0][0].id == (
        "employee-1"
    )

    assert batches[0][1].id == (
        "employee-2"
    )

    assert batches[0][0].source == (
        "OFFICE.employee"
    )

    assert batches[0][0].source_type == (
        "mysql"
    )
def test_mysql_loader_invalid_batch_size():

    loader = MySQLLoader(
        database_name="OFFICE",
        table_name="employee",
    )

    try:
        list(
            loader.load_batches(
                batch_size=0
            )
        )
        assert False
    except ValueError as exc:
        assert (
            "batch_size must be greater than 0"
            in str(exc)
        )