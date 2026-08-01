"""Persistent local FAISS store with PDF content-version validation."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import faiss
import numpy as np

from app.rag.chunker import KnowledgeChunk

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.index: faiss.Index | None = None
        self.chunks: list[KnowledgeChunk] = []

    @property
    def _index_path(self) -> Path:
        return self.directory / "knowledge.faiss"

    @property
    def _metadata_path(self) -> Path:
        return self.directory / "knowledge.json"

    def load_if_current(self, fingerprint: str) -> bool:
        if not self._index_path.is_file() or not self._metadata_path.is_file():
            return False
        payload = json.loads(self._metadata_path.read_text(encoding="utf-8"))
        if payload.get("fingerprint") != fingerprint:
            return False
        self.index = faiss.read_index(str(self._index_path))
        self.chunks = [KnowledgeChunk(**chunk) for chunk in payload["chunks"]]
        logger.info("Vector DB loaded with %d chunks", len(self.chunks))
        return True

    def rebuild(self, chunks: list[KnowledgeChunk], embeddings: np.ndarray, fingerprint: str) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, str(self._index_path))
        self._metadata_path.write_text(json.dumps({"fingerprint": fingerprint, "chunks": [chunk.__dict__ for chunk in chunks]}), encoding="utf-8")
        self.index, self.chunks = index, chunks
        logger.info("Vector DB rebuilt with %d chunks", len(chunks))

    def search(self, embedding: np.ndarray, limit: int = 5) -> list[tuple[KnowledgeChunk, float]]:
        if self.index is None:
            raise RuntimeError("RAG vector store is not initialized.")
        scores, positions = self.index.search(np.asarray([embedding], dtype="float32"), limit)
        return [(self.chunks[position], float(score)) for score, position in zip(scores[0], positions[0]) if position >= 0]
