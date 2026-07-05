from __future__ import annotations

import re
from collections import Counter
from io import BytesIO
from typing import Iterable

from agents.schemas import LectureChunk


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}

MEDICAL_KEYWORDS = {
    "acute",
    "airway",
    "arterial",
    "blood",
    "bronchitis",
    "cardiac",
    "chronic",
    "clinical",
    "complication",
    "diagnosis",
    "dyspnea",
    "failure",
    "fever",
    "infection",
    "inflammation",
    "management",
    "obstruction",
    "patient",
    "pressure",
    "respiratory",
    "risk",
    "symptom",
    "therapy",
    "treatment",
}


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text)
        if token.lower() not in STOPWORDS
    ]


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", normalize_text(text))
    return [piece.strip() for piece in pieces if len(piece.strip()) > 30]


def extract_text_from_pdf(pdf_bytes: bytes) -> list[tuple[int, str]]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF upload support. Install requirements.txt.") from exc

    pages: list[tuple[int, str]] = []
    with fitz.open(stream=BytesIO(pdf_bytes), filetype="pdf") as document:
        for index, page in enumerate(document, start=1):
            text = normalize_text(page.get_text("text"))
            if text:
                pages.append((index, text))
    return pages


def chunk_text(text: str, source: str = "pasted_text", max_words: int = 130) -> list[LectureChunk]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    chunks: list[LectureChunk] = []
    current: list[str] = []
    current_words = 0

    def flush() -> None:
        nonlocal current, current_words
        if not current:
            return
        chunk_id = f"chunk_{len(chunks) + 1:03d}"
        chunks.append(LectureChunk(chunk_id=chunk_id, source=source, page=None, text="\n\n".join(current)))
        current = []
        current_words = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        if current_words + len(words) > max_words and current:
            flush()
        if len(words) > max_words:
            for start in range(0, len(words), max_words):
                current = [" ".join(words[start : start + max_words])]
                current_words = len(current[0].split())
                flush()
        else:
            current.append(paragraph)
            current_words += len(words)

    flush()
    return chunks


def chunk_pages(pages: Iterable[tuple[int, str]], source: str, max_words: int = 130) -> list[LectureChunk]:
    chunks: list[LectureChunk] = []
    for page_number, text in pages:
        page_chunks = chunk_text(text, source=source, max_words=max_words)
        for page_chunk in page_chunks:
            chunk_id = f"chunk_{len(chunks) + 1:03d}"
            chunks.append(
                LectureChunk(
                    chunk_id=chunk_id,
                    source=page_chunk.source,
                    page=page_number,
                    text=page_chunk.text,
                )
            )
    return chunks


def search_lecture(chunks: list[LectureChunk], query: str, limit: int = 6) -> list[LectureChunk]:
    if not chunks:
        return []
    query_tokens = tokenize(query)
    if not query_tokens:
        return chunks[:limit]

    scored: list[tuple[float, LectureChunk]] = []
    query_counter = Counter(query_tokens)
    for chunk in chunks:
        chunk_counter = Counter(tokenize(chunk.text))
        overlap = sum(min(chunk_counter[token], count) for token, count in query_counter.items())
        keyword_bonus = sum(1 for token in query_tokens if token in MEDICAL_KEYWORDS and token in chunk_counter)
        score = overlap + (0.75 * keyword_bonus)
        if score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
    return [chunk for _, chunk in scored[:limit]] or chunks[:limit]


def list_topics(chunks: list[LectureChunk], limit: int = 10) -> list[str]:
    token_counts = Counter()
    for chunk in chunks:
        token_counts.update(tokenize(chunk.text))

    for token in list(token_counts):
        if token in STOPWORDS or token.isdigit():
            del token_counts[token]

    prioritized = sorted(
        token_counts.items(),
        key=lambda item: (-(item[0] in MEDICAL_KEYWORDS), -item[1], item[0]),
    )
    return [token.replace("-", " ").title() for token, _ in prioritized[:limit]]


def chunk_citation(chunk: LectureChunk) -> str:
    page = f", page {chunk.page}" if chunk.page else ""
    return f"{chunk.chunk_id} ({chunk.source}{page})"

