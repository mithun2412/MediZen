"""Compact LangChain RAG pipeline for the MediZen knowledge base."""
from __future__ import annotations

from collections import OrderedDict
from hashlib import sha256
import json
import logging
import os
import re
from pathlib import Path
from threading import RLock
from time import perf_counter
from typing import Iterable

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)
FALLBACK = "I couldn't find that information in the MediZen AI knowledge base."
KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parents[1] / "knowledge" / "MediZen_AI_User_Knowledge_Base.txt"
INDEX_DIRECTORY = Path(__file__).resolve().parents[1] / "vector_store" / "langchain_knowledge_base"
INDEX_METADATA_PATH = INDEX_DIRECTORY / "metadata.json"
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def _is_heading(line: str) -> bool:
    """Identify short section headings before recursive chunking."""
    # The user guide is Markdown.  Strip its heading marker before applying
    # the lightweight heading heuristic, otherwise every FAQ is lumped into a
    # single anonymous document and retrieval loses the useful section title.
    compact = re.sub(r"^#{1,6}\s+", "", line.strip())
    if not compact or len(compact) > 120:
        return False
    return bool(re.match(r"^(\d+(?:\.\d+)*[.)]?\s+)?[A-Z][A-Za-z0-9 ,:&/()\-]{2,}$", compact)) and (
        compact.isupper() or bool(re.match(r"^\d", compact)) or len(compact.split()) <= 8
    )


def _plain_section_answer(document: Document) -> str:
    """Return a readable, source-grounded response without an LLM.

    This keeps product-help questions available when the optional Groq key is
    not configured or the provider is temporarily unavailable.
    """
    lines = [line.strip() for line in document.page_content.splitlines() if line.strip()]
    if lines and _is_heading(lines[0]):
        lines.pop(0)
    answer = " ".join(lines).strip()
    return answer or FALLBACK


def _section_documents(pages: Iterable[Document]) -> list[Document]:
    """Keep each PDF heading with its body before splitting long sections."""
    sections: list[Document] = []
    for page in pages:
        heading: str | None = None
        body: list[str] = []
        for raw_line in page.page_content.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line:
                continue
            if _is_heading(line):
                if body:
                    sections.append(Document(page_content="\n".join(filter(None, [heading, " ".join(body)])), metadata={**page.metadata, "heading": heading}))
                    body = []
                heading = line
            else:
                body.append(line)
        if body:
            sections.append(Document(page_content="\n".join(filter(None, [heading, " ".join(body)])), metadata={**page.metadata, "heading": heading}))
    return sections


class RAGService:
    """Load one knowledge-base PDF and answer only from retrieved chunks."""

    def __init__(self) -> None:
        self._vector_store: FAISS | None = None
        self._embeddings: HuggingFaceEmbeddings | None = None
        self._lock = RLock()
        self._knowledge_fingerprint: str | None = None
        self._answer_cache: OrderedDict[str, dict] = OrderedDict()
        self._retrieval_cache: OrderedDict[str, list[tuple[Document, float]]] = OrderedDict()

    def initialize(self) -> None:
        with self._lock:
            if not KNOWLEDGE_BASE_PATH.is_file():
                raise FileNotFoundError(f"Knowledge-base text file was not found: {KNOWLEDGE_BASE_PATH}")
            fingerprint = sha256(KNOWLEDGE_BASE_PATH.read_bytes()).hexdigest()
            if self._vector_store is not None and self._knowledge_fingerprint == fingerprint:
                return
            self._answer_cache.clear()
            self._retrieval_cache.clear()
            self._embeddings = self._embeddings or HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            if self._load_cached_index(fingerprint):
                self._knowledge_fingerprint = fingerprint
                return
            documents = TextLoader(str(KNOWLEDGE_BASE_PATH), encoding="utf-8").load()
            sections = _section_documents(documents)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            chunks = splitter.split_documents(sections)
            if not chunks:
                raise ValueError("No chunks could be created from the knowledge-base PDF.")
            self._vector_store = FAISS.from_documents(chunks, self._embeddings)
            INDEX_DIRECTORY.mkdir(parents=True, exist_ok=True)
            self._vector_store.save_local(str(INDEX_DIRECTORY))
            INDEX_METADATA_PATH.write_text(json.dumps({"fingerprint": fingerprint}), encoding="utf-8")
            self._knowledge_fingerprint = fingerprint
            logger.info("RAG initialized with %d documents, %d sections, and %d hybrid chunks", len(documents), len(sections), len(chunks))

    def _load_cached_index(self, fingerprint: str) -> bool:
        """Load the locally generated FAISS index only when the text file is unchanged."""
        if not INDEX_METADATA_PATH.is_file() or not (INDEX_DIRECTORY / "index.faiss").is_file():
            return False
        try:
            metadata = json.loads(INDEX_METADATA_PATH.read_text(encoding="utf-8"))
            if metadata.get("fingerprint") != fingerprint:
                return False
            assert self._embeddings is not None
            # This index is generated locally by this application; do not load
            # cache directories obtained from an untrusted source.
            self._vector_store = FAISS.load_local(
                str(INDEX_DIRECTORY),
                self._embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Loaded cached FAISS index from %s", INDEX_DIRECTORY)
            return True
        except Exception:
            logger.warning("Unable to load cached FAISS index; rebuilding it", exc_info=True)
            return False

    def _get_cached_answer(self, key: str) -> dict | None:
        with self._lock:
            result = self._answer_cache.get(key)
            if result is not None:
                self._answer_cache.move_to_end(key)
            return result

    def _cache_answer(self, key: str, result: dict) -> None:
        with self._lock:
            self._answer_cache[key] = result
            self._answer_cache.move_to_end(key)
            while len(self._answer_cache) > 256:
                self._answer_cache.popitem(last=False)

    def _retrieve(self, question: str) -> list[tuple[Document, float]]:
        key = " ".join(question.lower().split())
        with self._lock:
            cached = self._retrieval_cache.get(key)
            if cached is not None:
                self._retrieval_cache.move_to_end(key)
                return cached
        assert self._vector_store is not None
        results = self._vector_store.similarity_search_with_relevance_scores(question, k=5, score_threshold=0.28)
        with self._lock:
            self._retrieval_cache[key] = results
            self._retrieval_cache.move_to_end(key)
            while len(self._retrieval_cache) > 512:
                self._retrieval_cache.popitem(last=False)
        return results

    def answer(self, question: str) -> dict:
        if not question or not question.strip():
            return {"answer": FALLBACK, "sources": []}
        # Check for an appended or edited knowledge base before using cached data.
        self.initialize()
        key = " ".join(question.lower().split())
        if cached := self._get_cached_answer(key):
            return cached
        started = perf_counter()
        results = self._retrieve(question)
        logger.info("RAG retrieval completed in %.1fms", (perf_counter() - started) * 1000)
        if not results:
            result = {"answer": FALLBACK, "sources": []}
            self._cache_answer(key, result)
            return result
        context = "\n\n".join(
            f"[Section: {document.metadata.get('heading') or 'Knowledge base'}]\n{document.page_content}"
            for document, _ in results
        )
        generated_answer = self._generate(question, context)
        # A knowledge-base answer should not disappear merely because the
        # optional answer-writing model is offline.  Retrieval already found a
        # relevant, local section, so safely return that source material.
        if generated_answer == FALLBACK:
            generated_answer = _plain_section_answer(results[0][0])
        result = {
            "answer": generated_answer,
            "sources": list(dict.fromkeys(document.metadata.get("heading") or "Knowledge base" for document, _ in results)),
        }
        self._cache_answer(key, result)
        return result

    @staticmethod
    def _generate(question: str, context: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("RAG answer unavailable because GROQ_API_KEY is not configured")
            return FALLBACK
        try:
            from groq import Groq

            response = Groq(api_key=api_key).chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "Answer only from the retrieved MediZen AI knowledge-base context. If the answer is not explicitly available, reply exactly: I couldn't find that information in the MediZen AI knowledge base. Never invent features or add external knowledge."},
                    {"role": "user", "content": f"Question: {question}\n\nRetrieved context:\n{context}"},
                ],
            )
            return response.choices[0].message.content.strip() or FALLBACK
        except Exception:
            logger.exception("RAG LLM request failed")
            return FALLBACK


rag_service = RAGService()
