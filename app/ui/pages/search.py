"""Search page for InsightSphere."""

import streamlit as st

from app.search.search_service import SearchService


RESULT_LIMITS = [5, 10, 20]


def _flatten_results(results: dict) -> list[dict]:
    """Convert ChromaDB search results into individual result records."""

    ids = results.get("ids") or []
    documents = results.get("documents") or []
    metadatas = results.get("metadatas") or []
    distances = results.get("distances") or []

    # ChromaDB typically returns nested lists for query results.
    if ids and isinstance(ids[0], list):
        ids = ids[0]

    if documents and isinstance(documents[0], list):
        documents = documents[0]

    if metadatas and isinstance(metadatas[0], list):
        metadatas = metadatas[0]

    if distances and isinstance(distances[0], list):
        distances = distances[0]

    flattened = []

    for index, document_id in enumerate(ids):
        metadata = (
            metadatas[index]
            if index < len(metadatas) and metadatas[index]
            else {}
        )

        content = (
            documents[index]
            if index < len(documents)
            else ""
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        flattened.append(
            {
                "id": document_id,
                "content": content,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return flattened


def _render_search_result(result: dict, index: int) -> None:
    """Display one search result."""

    metadata = result["metadata"]
    source = metadata.get("source", "Unknown source")
    source_type = metadata.get("source_type", "Unknown")
    content = result["content"]
    distance = result["distance"]

    with st.container(border=True):
        st.markdown(f"**Result {index + 1}: {source}**")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption(f"Document type: {source_type}")

        with col2:
            if isinstance(distance, (int, float)):
                st.caption(f"Distance: {distance:.4f}")

        preview_length = 350
        preview = content[:preview_length]

        if len(content) > preview_length:
            preview += "..."

        st.write(preview)

        with st.expander("View full content and metadata"):
            st.text_area(
                "Document content",
                value=content,
                height=200,
                disabled=True,
                key=f"search_content_{index}_{result['id']}",
            )

            st.json(metadata)


def _render_results(results: list[dict]) -> None:
    """Display search results and filtering controls."""

    if not results:
        st.info("No matching documents were found.")
        return

    st.markdown(f"### Search results ({len(results)})")

    available_sources = sorted(
        {
            str(result["metadata"].get("source", "Unknown source"))
            for result in results
        }
    )

    available_types = sorted(
        {
            str(result["metadata"].get("source_type", "Unknown"))
            for result in results
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_sources = st.multiselect(
            "Filter by source",
            options=available_sources,
            default=available_sources,
            key="search_source_filter",
        )

    with col2:
        selected_types = st.multiselect(
            "Filter by document type",
            options=available_types,
            default=available_types,
            key="search_type_filter",
        )

    filtered_results = [
        result
        for result in results
        if str(
            result["metadata"].get("source", "Unknown source")
        ) in selected_sources
        and str(
            result["metadata"].get("source_type", "Unknown")
        ) in selected_types
    ]

    if not filtered_results:
        st.warning("No results match the selected filters.")
        return

    for index, result in enumerate(filtered_results):
        _render_search_result(result, index)


def render_search() -> None:
    """Render the InsightSphere semantic search page."""

    st.title("Search")
    st.caption(
        "Find relevant information across your ingested documents "
        "using semantic search."
    )

    with st.form("insightsphere_search_form"):
        query = st.text_input(
            "What are you looking for?",
            placeholder="Enter a question, topic, or phrase...",
        )

        n_results = st.selectbox(
            "Maximum results",
            options=RESULT_LIMITS,
            index=0,
        )

        search_submitted = st.form_submit_button(
            "Search documents",
            type="primary",
            use_container_width=True,
        )

    if search_submitted:
        if not query.strip():
            st.warning("Enter a search query before continuing.")
        else:
            try:
                with st.spinner("Searching your documents..."):
                    service = SearchService()
                    raw_results = service.search(
                        query=query,
                        n_results=n_results,
                    )

                flattened_results = _flatten_results(raw_results)

                st.session_state["insightsphere_search_results"] = (
                    flattened_results
                )
                st.session_state["insightsphere_search_query"] = query
                st.session_state["insightsphere_search_error"] = None

                st.session_state.pop("search_source_filter", None)
                st.session_state.pop("search_type_filter", None)

            except Exception as exc:
                st.session_state["insightsphere_search_error"] = str(exc)
                st.session_state.pop(
                    "insightsphere_search_results",
                    None,
                )

    error = st.session_state.get("insightsphere_search_error")

    if error:
        st.error(f"Search failed: {error}")
        return

    previous_query = st.session_state.get(
        "insightsphere_search_query"
    )

    if previous_query:
        st.caption(f"Current query: {previous_query}")

    results = st.session_state.get(
        "insightsphere_search_results",
        [],
    )

    if results:
        _render_results(results)
    elif not search_submitted:
        st.info(
            "Enter a query above to search the documents "
            "available in your workspace."
        )