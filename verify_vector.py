from app.storage.vector_storage import VectorStorage


def main():

    storage = VectorStorage(
        collection_name="documents"
    )

    print("=" * 60)
    print("VECTOR DATABASE VERIFICATION")
    print("=" * 60)

    print(
        f"Stored documents: {storage.count()}"
    )

    results = storage.search(
        query="Alice Bengaluru",
        n_results=1,
    )

    print("\nSearch results:")

    print(results)


if __name__ == "__main__":
    main()