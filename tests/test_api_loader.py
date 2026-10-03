import pytest

from app.loaders.api_loader import APILoader


class FakeResponse:

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


def test_api_loader(monkeypatch):

    def fake_get(*args, **kwargs):

        return FakeResponse(
            [
                {
                    "customer_id": 101,
                    "name": "Alice",
                },
                {
                    "customer_id": 102,
                    "name": "Bob",
                },
            ]
        )

    monkeypatch.setattr(
        "app.loaders.api_loader.requests.get",
        fake_get,
    )

    loader = APILoader()

    documents = loader.load(
        "https://example.com/api/customers"
    )

    assert len(documents) == 2

    assert documents[0].id == "api-1"

    assert documents[0].source_type == "api"

    assert documents[0].metadata["row_number"] == 1

    assert "customer_id" in (
        documents[0].metadata["columns"]
    )


def test_api_loader_batches(monkeypatch):

    def fake_get(url, params=None, **kwargs):

        page = params["page"]

        if page == 1:

            return FakeResponse(
                [
                    {
                        "customer_id": 101,
                        "name": "Alice",
                    },
                    {
                        "customer_id": 102,
                        "name": "Bob",
                    },
                ]
            )

        if page == 2:

            return FakeResponse(
                [
                    {
                        "customer_id": 103,
                        "name": "Charlie",
                    },
                    {
                        "customer_id": 104,
                        "name": "David",
                    },
                ]
            )

        return FakeResponse([])

    monkeypatch.setattr(
        "app.loaders.api_loader.requests.get",
        fake_get,
    )

    loader = APILoader()

    batches = list(
        loader.load_batches(
            "https://example.com/api/customers",
            page_size=2,
        )
    )

    assert len(batches) == 2

    assert len(batches[0]) == 2

    assert len(batches[1]) == 2

    assert batches[0][0].id == "api-1"

    assert batches[1][0].id == "api-3"

    assert batches[0][0].metadata["page"] == 1

    assert batches[1][0].metadata["page"] == 2


def test_api_loader_invalid_page_size():

    loader = APILoader()

    with pytest.raises(ValueError):

        list(
            loader.load_batches(
                "https://example.com/api",
                page_size=0,
            )
        )