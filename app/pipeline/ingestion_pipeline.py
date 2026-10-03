from app.models.document import Document


class IngestionPipeline:
    """
    Main processing pipeline.
    """

    def run(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Process ingested documents.
        """

        print(
            f"Pipeline received {len(documents)} document(s)"
        )

        return documents