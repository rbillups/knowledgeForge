class DocumentProcessingError(Exception):
    """Raised when document text extraction or chunking fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UnsupportedFileTypeError(Exception):
    """Raised when an uploaded file type is not supported."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.message = (
            "Unsupported file type. Allowed types: PDF, TXT, and Markdown."
        )
        super().__init__(self.message)


class CollectionNotFoundError(Exception):
    """Raised when a knowledge collection does not exist."""

    def __init__(self, collection_id: int) -> None:
        self.collection_id = collection_id
        self.message = f"Knowledge collection {collection_id} was not found."
        super().__init__(self.message)


class DocumentNotFoundError(Exception):
    """Raised when a document does not exist."""

    def __init__(self, document_id: int) -> None:
        self.document_id = document_id
        self.message = f"Document {document_id} was not found."
        super().__init__(self.message)


class DocumentDeletionError(Exception):
    """Raised when a document cannot be deleted."""

    def __init__(self, document_id: int) -> None:
        self.document_id = document_id
        self.message = (
            f"Document {document_id} could not be deleted. Please try again."
        )
        super().__init__(self.message)


class PortfolioKnowledgeBaseUnavailableError(Exception):
    """Raised when the portfolio collection is missing."""

    message = "The portfolio knowledge base is not available."

    def __init__(self) -> None:
        super().__init__(self.message)


class MissingApiKeyError(Exception):
    """Raised when the OpenAI API key is not configured."""

    message = (
        "OpenAI API key is not configured. Set OPENAI_API_KEY in the environment."
    )

    def __init__(self) -> None:
        super().__init__(self.message)


class EmbeddingGenerationError(Exception):
    """Raised when embedding generation fails."""

    def __init__(
        self,
        message: str = "Unable to generate embeddings at this time.",
    ) -> None:
        self.message = message
        super().__init__(message)


class ChatGenerationError(Exception):
    """Raised when grounded chat generation fails."""

    def __init__(
        self,
        message: str = "Unable to generate a chat response at this time.",
    ) -> None:
        self.message = message
        super().__init__(message)
