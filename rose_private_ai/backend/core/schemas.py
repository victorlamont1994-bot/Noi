from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    top_k: int | None = None
    strict_sources: bool | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5


class SearchHit(BaseModel):
    text: str
    metadata: dict[str, Any]
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    sources: list[SearchHit] = []
    model: str
