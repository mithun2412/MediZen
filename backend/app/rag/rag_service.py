"""Application-facing RAG service for answers grounded exclusively in the PDF."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from time import perf_counter

from app.rag.chunker import chunk_pages
from app.rag.cache import LRUCache
from app.rag.embedding import embed_documents
from app.rag.loader import document_fingerprint, load_pdf
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)
FALLBACK = "I couldn't find that information in the MediZen AI knowledge base."
PDF_PATH = Path(__file__).resolve().parents[1] / "knowledge" / "MediZen_AI_User_Knowledge_Base.pdf"
STORE_PATH = Path(__file__).resolve().parents[1] / "vector_store"


class RAGService:
    def __init__(self) -> None:
        self.store = VectorStore(STORE_PATH)
        self.retriever = Retriever(self.store)
        self._answer_cache: LRUCache[dict] = LRUCache(max_size=256)

    def initialize(self) -> None:
        fingerprint = document_fingerprint(PDF_PATH)
        if self.store.load_if_current(fingerprint):
            return
        pages = list(load_pdf(PDF_PATH))
        logger.info("PDF loaded: %d pages", len(pages))
        chunks = chunk_pages(pages)
        if not chunks:
            raise ValueError("No chunks could be created from the knowledge-base PDF.")
        logger.info("Chunks created: %d", len(chunks))
        embeddings = embed_documents([chunk.text for chunk in chunks])
        logger.info("Embeddings generated: %d", len(embeddings))
        self.store.rebuild(chunks, embeddings, fingerprint)

    def answer(self, question: str) -> dict:
        if not question or not question.strip():
            return {"answer": FALLBACK, "sources": []}
        key = " ".join(question.lower().split())
        cached_answer = self._answer_cache.get(key)
        if cached_answer is not None:
            logger.info("RAG answer cache hit")
            return cached_answer
        if self.store.index is None:
            self.initialize()
        started = perf_counter()
        results, cache_hit = self.retriever.retrieve(question)
        logger.info("RAG retrieval %s in %.1fms", "cache hit" if cache_hit else "cache miss", (perf_counter() - started) * 1000)
        # A low similarity result is not reliable context and must not be used.
        if not results or results[0][1] < 0.28:
            result = {"answer": FALLBACK, "sources": []}
            self._answer_cache.set(key, result)
            return result
        context = "\n\n".join(f"[Page {chunk.page_number}]\n{chunk.text}" for chunk, _ in results)
        answer = self._generate(question, context)
        result = {"answer": answer, "sources": list(dict.fromkeys(f"Page {chunk.page_number}" for chunk, _ in results))}
        self._answer_cache.set(key, result)
        return result

    @staticmethod
    def _generate(question: str, context: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("RAG answer unavailable because GROQ_API_KEY is not configured")
            return FALLBACK
        started = perf_counter()
        try:
            from groq import Groq
            response = Groq(api_key=api_key).chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "You answer ONLY using the retrieved MediZen AI knowledge-base context. If the answer is not explicitly available, reply exactly: I couldn't find that information in the MediZen AI knowledge base. Never invent features or add external knowledge."},
                    {"role": "user", "content": f"Question: {question}\n\nRetrieved context:\n{context}"},
                ],
            )
            logger.info("RAG LLM completed in %.1fms", (perf_counter() - started) * 1000)
            return response.choices[0].message.content.strip() or FALLBACK
        except Exception:
            logger.exception("RAG LLM request failed")
            return FALLBACK


rag_service = RAGService()
