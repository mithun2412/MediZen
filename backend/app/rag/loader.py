"""PDF loading primitives for the MediZen knowledge base."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable

from PyPDF2 import PdfReader


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


def document_fingerprint(path: Path) -> str:
    """Return a content hash so a changed PDF reliably triggers a rebuild."""
    return sha256(path.read_bytes()).hexdigest()


def load_pdf(path: Path) -> Iterable[PageText]:
    if not path.is_file():
        raise FileNotFoundError(f"Knowledge-base PDF was not found: {path}")

    reader = PdfReader(str(path))
    pages = [
        PageText(page_number=index, text=(page.extract_text() or "").strip())
        for index, page in enumerate(reader.pages, start=1)
    ]
    if not any(page.text for page in pages):
        raise ValueError("The knowledge-base PDF does not contain extractable text.")
    return pages
