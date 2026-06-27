from pathlib import Path

from pypdf import PdfReader

from app.services.exceptions import DocumentProcessingError


def extract_text(file_path: Path, file_type: str) -> tuple[str, int | None]:
    if file_type == "pdf":
        return _extract_pdf_text(file_path)
    if file_type in {"txt", "markdown"}:
        return _extract_plain_text(file_path), None

    raise DocumentProcessingError(
        f"Text extraction is not supported for file type '{file_type}'."
    )


def _extract_pdf_text(file_path: Path) -> tuple[str, int]:
    try:
        reader = PdfReader(str(file_path))
    except Exception as exc:
        raise DocumentProcessingError(
            "Unable to read the uploaded PDF file."
        ) from exc

    page_texts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_texts.append(page_text.strip())

    combined_text = "\n\n".join(text for text in page_texts if text)
    if not combined_text.strip():
        raise DocumentProcessingError(
            "The uploaded PDF does not contain extractable text."
        )

    return combined_text, len(reader.pages)


def _extract_plain_text(file_path: Path) -> str:
    try:
        text = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentProcessingError(
            "The uploaded text file must be valid UTF-8."
        ) from exc
    except OSError as exc:
        raise DocumentProcessingError(
            "Unable to read the uploaded text file."
        ) from exc

    if not text.strip():
        raise DocumentProcessingError(
            "The uploaded text file is empty."
        )

    return text
