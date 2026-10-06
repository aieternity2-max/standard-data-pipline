from app.ai.classifier import DocumentClassifier
from app.ai.extractor import DocumentExtractor
from app.embeddings.embedding_service import EmbeddingService
from app.models.document import Document


class AIProcessor:
    """
    Coordinates document classification, extraction,
    and embedding preparation.
    """

    def __init__(self):

        self.classifier = DocumentClassifier()

        self.extractor = DocumentExtractor()

        self.embedding_service = EmbeddingService()

    def process(
        self,
        document: Document,
    ) -> dict:
        """
        Process a document through the AI services.

        Returns
        -------
        dict
            Combined classification, extraction,
            and embedding information.
        """

        if not isinstance(
            document,
            Document,
        ):
            raise TypeError(
                "document must be a Document instance"
            )

        classification = (
            self.classifier.classify(
                document.source_type
            )
        )

        extracted = (
            self.extractor.extract(
                document
            )
        )

        embedding_text = (
            self.embedding_service.prepare_text(
                document.content
            )
        )

        return {
            "document_id": document.id,
            "classification": classification,
            "extracted": extracted,
            "embedding_text": embedding_text,
        }