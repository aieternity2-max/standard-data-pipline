import sys

from app.loaders.loader_factory import LoaderFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline


def main() -> None:

    print("=" * 60)
    print("Standard Data Pipeline")
    print("=" * 60)

    # -----------------------------------------
    # 1. Check input argument
    # -----------------------------------------

    if len(sys.argv) < 2:

        print("Usage:")
        print("  python -m app.main <file_path>")

        return

    input_file = sys.argv[1]

    print(f"Input file: {input_file}")

    # -----------------------------------------
    # 2. Select loader
    # -----------------------------------------

    print("\nSelecting loader...")

    try:

        loader = LoaderFactory.get_loader(
            input_file
        )

    except Exception as error:

        print(
            "\nERROR: Failed to select loader."
        )

        print(
            f"Details: {error}"
        )

        print(
            "Pipeline execution stopped."
        )

        return

    print(
        f"Loader selected: "
        f"{loader.__class__.__name__}"
    )

    # -----------------------------------------
    # 3. Load documents
    # -----------------------------------------

    print("\nLoading documents...")

    try:

        documents = loader.load(
            input_file
        )

    except Exception as error:

        error_message = str(error)

        # -----------------------------------------
        # Empty CSV / empty input file
        # -----------------------------------------

        if (
            "No columns to parse from file"
            in error_message
        ):

            print(
                "Documents loaded: 0"
            )

            print(
                "\nWARNING: No documents were loaded."
            )

            print(
                "Pipeline execution stopped."
            )

            return

        # -----------------------------------------
        # Other loading errors
        # -----------------------------------------

        print(
            "\nERROR: Failed to load input file."
        )

        print(
            f"Details: {error_message}"
        )

        print(
            "Pipeline execution stopped."
        )

        return

    print(
        f"Documents loaded: {len(documents)}"
    )

    # -----------------------------------------
    # 4. Handle zero documents
    # -----------------------------------------

    if not documents:

        print(
            "\nWARNING: No documents were loaded."
        )

        print(
            "Pipeline execution stopped."
        )

        return

    # -----------------------------------------
    # 5. Start ingestion pipeline
    # -----------------------------------------

    print(
        "\nStarting ingestion pipeline..."
    )

    try:

        pipeline = IngestionPipeline()

        processed_documents = pipeline.run(
            documents
        )

    except Exception as error:

        print(
            "\nERROR: Pipeline execution failed."
        )

        print(
            f"Details: {error}"
        )

        print(
            "Pipeline execution stopped."
        )

        return

    # -----------------------------------------
    # 6. Data quality summary
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("DATA QUALITY SUMMARY")
    print("=" * 60)

    summary = (
        pipeline.last_quality_summary
    )

    print(
        f"Total records   : "
        f"{summary.total_records}"
    )

    print(
        f"Valid records   : "
        f"{summary.valid_records}"
    )

    print(
        f"Invalid records : "
        f"{summary.invalid_records}"
    )

    print(
        f"Quality score   : "
        f"{summary.quality_score:.2f}%"
    )

    # -----------------------------------------
    # 7. Processing summary
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    print(
        f"Processed documents : "
        f"{len(processed_documents)}"
    )

    # -----------------------------------------
    # 8. Storage summary
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("STORAGE SUMMARY")
    print("=" * 60)

    print(
        f"SQL records    : "
        f"{pipeline.last_sql_storage_count}"
    )

    print(
        f"Vector records : "
        f"{pipeline.last_vector_storage_count}"
    )

    # -----------------------------------------
    # 9. Display processed documents
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("PROCESSED DOCUMENTS")
    print("=" * 60)

    for document in processed_documents[:3]:

        print("-" * 60)

        print(
            f"ID: {document.id}"
        )

        print(
            f"Source: {document.source}"
        )

        print(
            f"Type: {document.source_type}"
        )

        print(
            f"Content: {document.content}"
        )

    # -----------------------------------------
    # 10. Completion message
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("INGESTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()