"""Explore Data page for InsightSphere."""

import streamlit as st
import pandas as pd

from app.storage.vector_storage import VectorStorage
from app.storage.sql_storage import SQLStorage
from app.search.search_service import SearchService


PAGE_SIZE = 20


def _get_vector_storage() -> VectorStorage:
    """Return the configured vector storage instance."""
    return VectorStorage()


def _render_storage_overview(
    vector_storage: VectorStorage,
) -> None:
    """Display storage counts and database connectivity."""

    st.subheader("Storage overview")

    columns = st.columns(2)

    try:
        document_count = vector_storage.count()

        columns[0].metric(
            "Indexed documents",
            document_count,
        )
    except Exception as exc:
        columns[0].error(
            "Unable to read the vector document count."
        )
        with columns[0].expander("Technical details"):
            st.code(str(exc))

    try:
        sql_storage = SQLStorage()
        connected = sql_storage.test_connection()

        if connected:
            columns[1].metric(
                "MySQL connection",
                "Connected",
            )
        else:
            columns[1].metric(
                "MySQL connection",
                "Unavailable",
            )
    except Exception as exc:
        columns[1].metric(
            "MySQL connection",
            "Unavailable",
        )

        with columns[1].expander("Connection details"):
            st.code(str(exc))


def _get_documents(
    vector_storage: VectorStorage,
    limit: int,
    offset: int = 0,
) -> dict:
    """Retrieve stored documents from ChromaDB."""

    return vector_storage.collection.get(
        limit=limit,
        offset=offset,
        include=["documents", "metadatas"],
    )


def _render_document_table(
    results: dict,
    key_prefix: str,
) -> None:
    """Display documents in a table and allow content inspection."""

    ids = results.get("ids") or []
    documents = results.get("documents") or []
    metadatas = results.get("metadatas") or []

    if not ids:
        st.info("No documents found.")
        return

    rows = []

    for index, document_id in enumerate(ids):
        metadata = (
            metadatas[index]
            if index < len(metadatas) and metadatas[index]
            else {}
        )

        content = (
            documents[index]
            if index < len(documents) and documents[index]
            else ""
        )

        rows.append(
            {
                "Document ID": document_id,
                "Source": metadata.get("source", "Unknown"),
                "Type": metadata.get("source_type", "Unknown"),
                "Content preview": content[:180],
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Document details")

    selected_id = st.selectbox(
        "Select a document",
        options=ids,
        format_func=lambda document_id: (
            f"{document_id} — "
            f"{rows[ids.index(document_id)]['Source']}"
        ),
        key=f"{key_prefix}_document_selection",
    )

    selected_index = ids.index(selected_id)

    st.text_area(
        "Document content",
        value=(
            documents[selected_index]
            if selected_index < len(documents)
            and documents[selected_index]
            else ""
        ),
        height=200,
        disabled=True,
        key=f"{key_prefix}_document_content",
    )

    selected_metadata = (
        metadatas[selected_index]
        if selected_index < len(metadatas)
        and metadatas[selected_index]
        else {}
    )

    with st.expander("View document metadata"):
        st.json(selected_metadata)


def _render_document_explorer(
    vector_storage: VectorStorage,
) -> None:
    """Browse documents stored in ChromaDB."""

    st.subheader("Document explorer")

    document_count = vector_storage.count()

    if document_count == 0:
        st.info(
            "No indexed documents are available yet. "
            "Upload files and run the ingestion pipeline first."
        )
        return

    page_count = max(
        1,
        (document_count + PAGE_SIZE - 1) // PAGE_SIZE,
    )

    page = st.number_input(
        "Page",
        min_value=1,
        max_value=page_count,
        value=1,
        step=1,
        key="insightsphere_explorer_page",
    )

    offset = (int(page) - 1) * PAGE_SIZE

    results = _get_documents(
        vector_storage,
        limit=PAGE_SIZE,
        offset=offset,
    )

    st.caption(
        f"Page {page} of {page_count} · "
        f"{document_count} indexed documents"
    )

    _render_document_table(
        results,
        key_prefix=f"browse_page_{page}",
    )


def _render_semantic_search() -> None:
    """Search stored documents using the existing SearchService."""

    st.subheader("Semantic search")

    query = st.text_input(
        "Search your documents",
        placeholder="Example: customer transactions or policy claims",
        key="insightsphere_explore_search_query",
    )

    result_count = st.selectbox(
        "Maximum results",
        options=[5, 10, 20],
        index=0,
        key="insightsphere_explore_search_limit",
    )

    if not st.button(
        "Search documents",
        type="primary",
        key="insightsphere_explore_search_button",
    ):
        return

    if not query.strip():
        st.warning("Enter a search query first.")
        return

    try:
        with st.spinner("Searching indexed documents..."):
            search_service = SearchService()

            results = search_service.search(
                query=query,
                n_results=result_count,
            )

        st.session_state["insightsphere_explore_search_results"] = results

        st.session_state["insightsphere_explore_search_query_submitted"] = (
            query
        )

    except Exception as exc:
        st.error("Document search failed.")

        with st.expander("Technical error details"):
            st.code(str(exc))

    results = st.session_state.get(
        "insightsphere_explore_search_results"
    )

    if results is None:
        return

    st.caption(
        "Results for: "
        + st.session_state.get(
            "insightsphere_explore_search_query_submitted",
            "",
        )
    )

    _render_document_table(
        results,
        key_prefix="semantic_search",
    )


def render_explore_data() -> None:
    """Render the Explore Data page."""

    st.title("Explore Data")

    st.caption(
        "Browse indexed documents, inspect metadata, and discover "
        "relevant information using semantic search."
    )

    try:
        vector_storage = _get_vector_storage()
    except Exception as exc:
        st.error("Unable to initialize vector storage.")

        with st.expander("Technical error details"):
            st.code(str(exc))

        return

    _render_storage_overview(vector_storage)

    st.divider()

    browsing_tab, search_tab = st.tabs(
        ["Browse documents", "Semantic search"]
    )

    with browsing_tab:
        try:
            _render_document_explorer(vector_storage)
        except Exception as exc:
            st.error("Unable to browse stored documents.")

            with st.expander("Technical error details"):
                st.code(str(exc))

    with search_tab:
        _render_semantic_search()