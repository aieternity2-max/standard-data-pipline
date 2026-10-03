import sys


from app.config.settings import settings
from app.loaders.loader_factory import LoaderFactory
from app.pipeline.ingestion_pipeline import IngestionPipeline


def main() -> None:
    print("=" * 60)
    print("Standard Data Pipeline")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m app.main <file_path>")
        return

    input_file = sys.argv[1]

    print(f"Input file: {input_file}")

    # Automatically select the correct loader
    loader = LoaderFactory.get_loader(input_file)

    # Load the input file
    documents = loader.load(input_file)

    print(f"Documents loaded: {len(documents)}")

    for document in documents[:3]:
        print("-" * 60)
        print(f"ID: {document.id}")
        print(f"Source: {document.source}")
        print(f"Type: {document.source_type}")
        print(f"Content: {document.content}")


if __name__ == "__main__":
    main()