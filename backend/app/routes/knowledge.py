"""Public API for MediZen user-guide questions grounded in the RAG PDF."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.rag.rag_service import rag_service

router = APIRouter()


class KnowledgeChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)


class KnowledgeChatResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("/chat", response_model=KnowledgeChatResponse)
def knowledge_chat(request: KnowledgeChatRequest) -> KnowledgeChatResponse:
    return KnowledgeChatResponse(**rag_service.answer(request.question))
