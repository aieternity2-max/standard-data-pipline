from app.config.settings import settings


def main() -> None:
    print("=" * 50)
    print(settings.app_name)
    print(f"Environment: {settings.environment}")
    print("Python engine initialized successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()

import sys

from app.config.settings import settings
from app.loaders.csv_loader import CSVLoader
from app.pipeline.ingestion_pipeline import IngestionPipeline


def main() -> None:
    print("=" * 60)
    print(settings.app_name)
    print("=" * 60)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m app.main <csv_file_path>")
        return

    csv_file = sys.argv[1]

    print(f"Input file: {csv_file}")

    loader = CSVLoader()

    documents = loader.load(csv_file)

    pipeline = IngestionPipeline()

    result = pipeline.run(documents)

    print(f"Records loaded: {len(result)}")

    for document in result[:3]:
        print("-" * 60)
        print(f"ID: {document.id}")
        print(f"Source: {document.source}")
        print(f"Type: {document.source_type}")
        print(f"Content: {document.content}")


if __name__ == "__main__":
    main()