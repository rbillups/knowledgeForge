import re

MIN_CHUNK_SIZE = 900
MAX_CHUNK_SIZE = 1200


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def chunk_text(text: str) -> list[str]:
    """Split text into readable chunks, preferring paragraph boundaries."""
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", normalized)
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current_parts: list[str] = []

    def current_length(parts: list[str]) -> int:
        return len("\n\n".join(parts)) if parts else 0

    def flush_current() -> None:
        if current_parts:
            chunks.append("\n\n".join(current_parts))

    for paragraph in paragraphs:
        if len(paragraph) > MAX_CHUNK_SIZE:
            if current_parts:
                chunks.append("\n\n".join(current_parts))
                current_parts = []
            chunks.extend(_split_long_paragraph(paragraph))
            continue

        projected_length = current_length(current_parts)
        if current_parts:
            projected_length += 2
        projected_length += len(paragraph)

        if current_parts and projected_length > MAX_CHUNK_SIZE:
            chunks.append("\n\n".join(current_parts))
            current_parts = [paragraph]
            continue

        current_parts.append(paragraph)

        if current_length(current_parts) >= MIN_CHUNK_SIZE:
            chunks.append("\n\n".join(current_parts))
            current_parts = []

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return _merge_small_trailing_chunk(chunks)


def _split_long_paragraph(paragraph: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    if len(sentences) <= 1:
        return _hard_split(paragraph)

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) > MAX_CHUNK_SIZE and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate

    if current:
        if len(current) > MAX_CHUNK_SIZE:
            chunks.extend(_hard_split(current))
        else:
            chunks.append(current)

    return chunks


def _hard_split(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + MAX_CHUNK_SIZE, len(text))
        if end < len(text):
            split_at = text.rfind(" ", start, end)
            if split_at > start + MIN_CHUNK_SIZE // 2:
                end = split_at
        chunks.append(text[start:end].strip())
        start = end
        if start < len(text) and text[start] == " ":
            start += 1
    return [chunk for chunk in chunks if chunk]


def _merge_small_trailing_chunk(chunks: list[str]) -> list[str]:
    if len(chunks) < 2:
        return chunks

    if len(chunks[-1]) >= MIN_CHUNK_SIZE // 2:
        return chunks

    merged = chunks[-2] + "\n\n" + chunks[-1]
    if len(merged) <= MAX_CHUNK_SIZE:
        return [*chunks[:-2], merged]

    return chunks
