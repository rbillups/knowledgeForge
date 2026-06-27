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
