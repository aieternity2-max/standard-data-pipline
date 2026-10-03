from pathlib import Path
from typing import Any

import requests

from app.loaders.base import BaseLoader
from app.models.document import Document


class APILoader(BaseLoader):
    """
    Loader for REST APIs.

    Supports:
    1. Normal API loading using load()
    2. Paginated batch loading using load_batches()
    """

    def load(
        self,
        source: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> list[Document]:
        """
        Load records from an API.

        The API response must contain a list of records,
        either directly or inside a 'data' field.
        """

        response = self._request(
            source,
            params=params,
            headers=headers,
        )

        data = response.json()

        records = self._extract_records(data)

        documents = []

        for row_number, record in enumerate(
            records,
            start=1,
        ):

            document = Document(
                id=f"api-{row_number}",
                source=source,
                source_type="api",
                content=str(record),
                metadata={
                    "row_number": row_number,
                    "columns": list(record.keys()),
                    "url": source,
                },
            )

            documents.append(document)

        return documents

    def load_batches(
        self,
        source: str,
        page_size: int = 100,
        max_pages: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        """
        Load API records page-by-page.

        Each API response is treated as one batch.

        This avoids loading a large API dataset
        into memory at once.
        """

        if page_size <= 0:
            raise ValueError(
                "page_size must be greater than 0"
            )

        page = 1
        total_records = 0

        while True:

            params = {
                "page": page,
                "limit": page_size,
            }

            response = self._request(
                source,
                params=params,
                headers=headers,
            )

            data = response.json()

            records = self._extract_records(data)

            if not records:
                break

            documents = []

            for record in records:

                total_records += 1

                document = Document(
                    id=f"api-{total_records}",
                    source=source,
                    source_type="api",
                    content=str(record),
                    metadata={
                        "row_number": total_records,
                        "columns": list(record.keys()),
                        "url": source,
                        "page": page,
                    },
                )

                documents.append(document)

            yield documents

            # If fewer records than requested were returned,
            # assume this is the final page.
            if len(records) < page_size:
                break

            page += 1

            if (
                max_pages is not None
                and page > max_pages
            ):
                break

    @staticmethod
    def _request(
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """
        Make an HTTP GET request with basic error handling.
        """

        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()

            return response

        except requests.RequestException as exc:

            raise RuntimeError(
                f"API request failed: {url}"
            ) from exc

    @staticmethod
    def _extract_records(
        data: Any,
    ) -> list[dict[str, Any]]:
        """
        Extract a list of dictionary records from
        common API response formats.
        """

        # Format 1:
        # [
        #     {...},
        #     {...}
        # ]

        if isinstance(data, list):

            records = data

        # Format 2:
        # {
        #     "data": [
        #         {...},
        #         {...}
        #     ]
        # }

        elif isinstance(data, dict):

            records = data.get("data")

            if records is None:
                raise ValueError(
                    "API response does not contain a 'data' field"
                )

        else:

            raise ValueError(
                "API response must be a list or dictionary"
            )

        if not isinstance(records, list):

            raise ValueError(
                "API records must be a list"
            )

        for index, record in enumerate(
            records,
            start=1,
        ):

            if not isinstance(record, dict):

                raise ValueError(
                    f"API record {index} must be an object"
                )

        return records