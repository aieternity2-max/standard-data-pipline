from app.loaders.loader_factory import LoaderFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline


def main():

    # -----------------------------------------
    # 1. Create MySQL loader
    # -----------------------------------------

    loader = LoaderFactory.get_mysql_loader(
        database_name="OFFICE",
        table_name="employee",
    )

    # -----------------------------------------
    # 2. Create ingestion pipeline
    # -----------------------------------------

    pipeline = IngestionPipeline()

    # -----------------------------------------
    # 3. Load MySQL records in batches
    #    and process them through the pipeline
    # -----------------------------------------

    processed_documents = pipeline.run_batches(
        loader.load_batches(
            batch_size=10
        )
    )

    # -----------------------------------------
    # 4. Print final results
    # -----------------------------------------

    print(
        f"Processed documents: "
        f"{len(processed_documents)}"
    )

    print(
        f"SQL records: "
        f"{pipeline.last_sql_storage_count}"
    )

    print(
        f"Vector records: "
        f"{pipeline.last_vector_storage_count}"
    )


if __name__ == "__main__":
    main()