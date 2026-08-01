"""Cached embeddings backed by the project's SentenceTransformer dependency."""
from __future__ import annotations

import logging
import os
from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.cache import LRUCache

logger = logging.getLogger(__name__)
MODEL_NAME = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_model: SentenceTransformer | None = None
_lock = Lock()
_query_cache: LRUCache[np.ndarray] = LRUCache(max_size=512)


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                logger.info("Loading RAG embedding model: %s", MODEL_NAME)
                _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_documents(texts: list[str]) -> np.ndarray:
    return _get_model().encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")


def embed_query(question: str) -> tuple[np.ndarray, bool]:
    key = " ".join(question.lower().split())
    cached = _query_cache.get(key)
    if cached is not None:
        return cached, True
    embedding = embed_documents([question])[0]
    _query_cache.set(key, embedding)
    return embedding, False
