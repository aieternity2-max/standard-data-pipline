import tempfile
from pathlib import Path

import streamlit as st

from app.config.settings import settings
from app.loaders.loader_factory import LoaderFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline


SUPPORTED_EXTENSIONS = [
    "csv",
    "xlsx",
    "xls",
    "json",
    "jsonl",
    "pdf",
    "docx",
    "txt",
]

PREVIEW_LIMIT = 10
JSONL_BATCH_SIZE = 1000


def _load_uploaded_files(uploaded_files):
    """Load uploaded files into Documents without running the pipeline."""

    all_documents = []
    file_results = []
    loading_errors = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        with tempfile.TemporaryDirectory(
            prefix="insightsphere_upload_"
        ) as temporary_directory:

            temporary_path = Path(temporary_directory)

            for index, uploaded_file in enumerate(
                uploaded_files,
                start=1,
            ):
                status_text.info(
                    f"Loading file {index} of {len(uploaded_files)}: "
                    f"{uploaded_file.name}"
                )

                try:
                    suffix = Path(uploaded_file.name).suffix.lower()

                    temporary_file = temporary_path / (
                        f"file_{index}{suffix}"
                    )

                    temporary_file.write_bytes(
                        uploaded_file.getvalue()
                    )

                    loader = LoaderFactory.get_loader(temporary_file)

                    if suffix == ".jsonl":
                        documents = []

                        for batch in loader.load_batches(
                            temporary_file,
                            batch_size=JSONL_BATCH_SIZE,
                        ):
                            documents.extend(batch)
                    else:
                        documents = loader.load(temporary_file)

                    for document in documents:
                        document.source = uploaded_file.name

                        metadata = dict(document.metadata or {})
                        metadata["file_name"] = uploaded_file.name
                        document.metadata = metadata

                    all_documents.extend(documents)

                    file_results.append(
                        {
                            "File": uploaded_file.name,
                            "Status": (
                                "Loaded"
                                if documents
                                else "No documents produced"
                            ),
                            "Documents": len(documents),
                        }
                    )

                except Exception as exc:
                    loading_errors.append(
                        {
                            "file": uploaded_file.name,
                            "error": str(exc),
                        }
                    )

                    file_results.append(
                        {
                            "File": uploaded_file.name,
                            "Status": "Failed to load",
                            "Documents": 0,
                        }
                    )

                progress_bar.progress(
                    index / len(uploaded_files)
                )

    finally:
        status_text.empty()
        progress_bar.empty()

    return all_documents, file_results, loading_errors


def _render_document_preview(documents):
    """Display a preview of the loaded documents."""

    st.subheader("Document preview")

    st.caption(
        f"{len(documents)} document(s) loaded. "
        "Review the preview before ingestion."
    )

    preview_rows = [
        {
            "Document ID": document.id,
            "Source": document.source,
            "Type": document.source_type,
            "Content preview": document.content[:200],
        }
        for document in documents[:PREVIEW_LIMIT]
    ]

    st.dataframe(
        preview_rows,
        use_container_width=True,
        hide_index=True,
    )

    if len(documents) > PREVIEW_LIMIT:
        st.caption(
            f"Showing the first {PREVIEW_LIMIT} of "
            f"{len(documents)} documents."
        )


def _render_ingestion_results(
    pipeline,
    input_document_count,
    processed_documents,
):
    """Display the existing pipeline's results."""

    st.success("Ingestion pipeline completed.")

    st.subheader("Ingestion summary")

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Input documents",
        input_document_count,
    )

    metric_columns[1].metric(
        "Processed documents",
        len(processed_documents),
    )

    metric_columns[2].metric(
        "SQL records",
        pipeline.last_sql_storage_count,
    )

    metric_columns[3].metric(
        "Vector records",
        pipeline.last_vector_storage_count,
    )

    invalid_documents = pipeline.last_invalid_documents
    invalid_count = len(invalid_documents)

    st.subheader("Validation results")

    if invalid_count:
        st.warning(
            f"{invalid_count} document(s) failed validation."
        )

        with st.expander("View invalid documents"):
            for document in invalid_documents:
                st.write(
                    {
                        "id": document.id,
                        "source": document.source,
                        "source_type": document.source_type,
                    }
                )
    else:
        st.success("No invalid documents were reported.")

    quality_summary = pipeline.last_quality_summary

    if quality_summary is not None:
        st.subheader("Data quality summary")

        quality_columns = st.columns(3)

        quality_columns[0].metric(
            "Quality score",
            f"{quality_summary.quality_score:.2f}",
        )

        quality_columns[1].metric(
            "Valid records",
            quality_summary.valid_records,
        )

        quality_columns[2].metric(
            "Invalid records",
            quality_summary.invalid_records,
        )

    if pipeline.last_ai_failures:
        with st.expander("AI processing warnings"):
            for failure in pipeline.last_ai_failures:
                st.warning(
                    f"Document {failure.get('document_id')}: "
                    f"{failure.get('error')}"
                )


def render_upload_data() -> None:
    """Render the staged file-preview and ingestion workflow."""

    st.title("Upload Data")

    st.caption(
        "Upload structured files and documents, preview their contents, "
        "and then run the standardized ingestion pipeline."
    )

    with st.container(border=True):
        st.subheader("Supported file formats")

        st.markdown(
            """
            **Structured data:** CSV, Excel, JSON, JSONL

            **Documents:** PDF, DOCX, TXT
            """
        )

    uploaded_files = st.file_uploader(
        "Choose one or more files",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
        help=(
            "Select CSV, Excel, JSON, JSONL, PDF, DOCX, or TXT files."
        ),
        key="insightsphere_uploaded_files",
    )

    if not uploaded_files:
        st.info(
            "Upload files to begin. You can preview their contents "
            "before sending them through the ingestion pipeline."
        )

        st.session_state.pop("insightsphere_preview_documents", None)
        st.session_state.pop("insightsphere_preview_file_results", None)
        st.session_state.pop("insightsphere_preview_errors", None)

        return

    st.subheader("Selected files")

    total_size = sum(
        uploaded_file.size
        for uploaded_file in uploaded_files
    )

    metric_columns = st.columns(2)

    metric_columns[0].metric(
        "Files selected",
        len(uploaded_files),
    )

    metric_columns[1].metric(
        "Total upload size",
        f"{total_size / (1024 * 1024):.2f} MB",
    )

    file_rows = [
        {
            "File name": uploaded_file.name,
            "Format": Path(uploaded_file.name).suffix.upper(),
            "Size (KB)": round(uploaded_file.size / 1024, 2),
        }
        for uploaded_file in uploaded_files
    ]

    st.dataframe(
        file_rows,
        use_container_width=True,
        hide_index=True,
    )

    current_signature = tuple(
        (
            uploaded_file.name,
            uploaded_file.size,
        )
        for uploaded_file in uploaded_files
    )

    previous_signature = st.session_state.get(
        "insightsphere_preview_signature"
    )

    if current_signature != previous_signature:
        st.session_state.pop(
            "insightsphere_preview_documents",
            None,
        )
        st.session_state.pop(
            "insightsphere_preview_file_results",
            None,
        )
        st.session_state.pop(
            "insightsphere_preview_errors",
            None,
        )
        st.session_state.pop(
            "insightsphere_preview_signature",
            None,
        )

    if st.button(
        "Preview Files",
        type="primary",
        use_container_width=True,
        key="insightsphere_preview_button",
    ):
        documents, file_results, loading_errors = (
            _load_uploaded_files(uploaded_files)
        )

        st.session_state["insightsphere_preview_documents"] = documents
        st.session_state["insightsphere_preview_file_results"] = file_results
        st.session_state["insightsphere_preview_errors"] = loading_errors
        st.session_state["insightsphere_preview_signature"] = (
            current_signature
        )

        # A new preview requires a new explicit ingestion action.
        st.session_state.pop("insightsphere_last_ingestion", None)

    documents = st.session_state.get(
        "insightsphere_preview_documents"
    )

    if documents is None:
        st.info(
            "Select Preview Files to load and inspect your documents. "
            "This step does not execute the ingestion pipeline."
        )
        return

    st.subheader("File loading results")

    st.dataframe(
        st.session_state["insightsphere_preview_file_results"],
        use_container_width=True,
        hide_index=True,
    )

    loading_errors = st.session_state["insightsphere_preview_errors"]

    if loading_errors:
        with st.expander("Review file loading errors", expanded=True):
            for error in loading_errors:
                st.error(
                    f"{error['file']}: {error['error']}"
                )

    if not documents:
        st.error(
            "No documents could be loaded. Correct the file errors "
            "and preview the files again."
        )
        return

    _render_document_preview(documents)

    st.warning(
        "The preview has not been ingested. Clicking Ingest Data "
        "will execute the pipeline and write processed records to "
        "your configured SQL and vector storage."
    )

    if st.button(
        "Ingest Data",
        type="primary",
        use_container_width=True,
        key="insightsphere_ingest_button",
    ):
        try:
            pipeline = IngestionPipeline()

            with st.spinner(
                "Validating, processing, embedding, and storing documents..."
            ):
                processed_documents = pipeline.run(documents)

            st.session_state["insightsphere_last_ingestion"] = {
                "uploaded_files": [
                    uploaded_file.name
                    for uploaded_file in uploaded_files
                ],
                "input_document_count": len(documents),
                "processed_document_count": len(processed_documents),
                "invalid_document_count": len(
                    pipeline.last_invalid_documents
                ),
                "sql_storage_count": pipeline.last_sql_storage_count,
                "vector_storage_count": pipeline.last_vector_storage_count,
                "quality_summary": pipeline.last_quality_summary,
                "file_results": st.session_state[
                    "insightsphere_preview_file_results"
                ],
                "loading_errors": loading_errors,
            }

            st.subheader("Pipeline execution")

            _render_ingestion_results(
                pipeline,
                len(documents),
                processed_documents,
            )

        except Exception as exc:
            st.error(
                "The ingestion pipeline failed. Review the error "
                "details before attempting another ingestion."
            )

            with st.expander(
                "Technical error details",
                expanded=True,
            ):
                st.code(str(exc))