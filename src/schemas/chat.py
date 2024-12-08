from typing import Optional

from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    queue_time: float
    prompt_time: float
    completion_time: float
    total_time: float


class ChatMessage(BaseModel):
    role: str
    content: str
    usage: Optional[TokenUsage] = None


class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None


class ChatResponse(BaseModel):
    response: ChatMessage
