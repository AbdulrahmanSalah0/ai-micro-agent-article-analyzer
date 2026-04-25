# agent/processor.py

def clean_text(text: str) -> str:
    """Normalize whitespace."""
    return " ".join(text.split())


def validate_text(text: str) -> bool:
    """Ensure text is valid."""
    return bool(text and len(text) > 200)


def chunk_text(text: str, max_length: int = 2000, overlap: int = 100) -> list:
    """
    Split text into overlapping chunks.
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        start += max_length - overlap

    return chunks


def select_representative_chunks(chunks: list) -> list:
    """
    Select 3 smart chunks:
    - First
    - Middle
    - Before last (not last!)
    """

    if len(chunks) <= 3:
        return chunks

    return [
        chunks[0],
        chunks[len(chunks) // 2],
        chunks[-2]  # 🔥 instead of last
    ]