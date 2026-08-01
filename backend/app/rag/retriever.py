"""Top-k retrieval over the MediZen knowledge-base vector store."""
from __future__ import annotations

import re

from app.rag.cache import LRUCache
from app.rag.embedding import embed_query
from app.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore) -> None:
        self.store = store
        self._cache: LRUCache[list[tuple[object, float]]] = LRUCache(max_size=256)
        self._similar_queries: list[tuple[str, set[str], list[tuple[object, float]]]] = []

    @staticmethod
    def _tokens(question: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9]+", question.lower()) if len(token) > 2}

    def retrieve(self, question: str, limit: int = 5):
        key = " ".join(question.lower().split())
        cached = self._cache.get(key)
        if cached is not None:
            return cached, True
        tokens = self._tokens(question)
        for _, prior_tokens, prior_results in self._similar_queries:
            union = tokens | prior_tokens
            if union and len(tokens & prior_tokens) / len(union) >= 0.8:
                self._cache.set(key, prior_results)
                return prior_results, True
        embedding, _ = embed_query(question)
        results = self.store.search(embedding, limit)
        self._cache.set(key, results)
        self._similar_queries.append((key, tokens, results))
        self._similar_queries = self._similar_queries[-128:]
        return results, False
