from app.services.chunking import MAX_CHUNK_SIZE, MIN_CHUNK_SIZE, chunk_text


def test_chunk_text_returns_empty_list_for_blank_input() -> None:
    assert chunk_text("") == []
    assert chunk_text("   \n\n   ") == []


def test_chunk_text_preserves_paragraph_boundaries() -> None:
    paragraphs = [
        "A" * 500,
        "B" * 500,
        "C" * 500,
    ]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert MIN_CHUNK_SIZE // 2 <= len(chunk) <= MAX_CHUNK_SIZE + 200
    assert "A" * 500 in chunks[0]
    assert "\n\n" in text


def test_chunk_text_splits_long_paragraphs() -> None:
    text = "Word " * 400
    chunks = chunk_text(text.strip())

    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= MAX_CHUNK_SIZE


def test_chunk_text_combines_short_paragraphs() -> None:
    paragraphs = ["Short paragraph one.", "Short paragraph two."] * 80
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text)

    assert chunks
    assert all(len(chunk) <= MAX_CHUNK_SIZE for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) >= len(text) - 50
