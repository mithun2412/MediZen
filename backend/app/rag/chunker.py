"""Semantic-ish, heading-preserving chunks for the compact user guide."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from app.rag.loader import PageText

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    text: str
    page_number: int
    heading: str | None = None


def _is_heading(line: str) -> bool:
    compact = line.strip()
    if not compact or len(compact) > 120:
        return False
    return bool(re.match(r"^(\d+(?:\.\d+)*[.)]?\s+)?[A-Z][A-Za-z0-9 ,:&/()\-]{2,}$", compact)) and (
        compact.isupper() or bool(re.match(r"^\d", compact)) or len(compact.split()) <= 8
    )


def _sections(page: PageText) -> Iterable[tuple[str | None, str]]:
    heading: str | None = None
    buffer: list[str] = []
    for raw_line in page.text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        if _is_heading(line):
            if buffer:
                yield heading, " ".join(buffer)
                buffer = []
            heading = line
        else:
            buffer.append(line)
    if buffer:
        yield heading, " ".join(buffer)


def _windows(text: str) -> Iterable[str]:
    """Prefer sentence boundaries while retaining an overlap between windows."""
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        if end < len(text):
            boundary = max(text.rfind(". ", start, end), text.rfind("? ", start, end), text.rfind("! ", start, end))
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary + 1
        yield text[start:end].strip()
        if end >= len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)


def chunk_pages(pages: Iterable[PageText]) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for page in pages:
        for heading, body in _sections(page):
            prefix = f"{heading}\n" if heading else ""
            for text in _windows(body):
                content = f"{prefix}{text}".strip()
                chunks.append(KnowledgeChunk(str(len(chunks)), content, page.page_number, heading))
    return chunks
