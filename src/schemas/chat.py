from typing import Optional

from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    queue_time: Optional[float] = None
    prompt_time: Optional[float] = None
    completion_time: Optional[float] = None
    total_time: Optional[float] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    usage: Optional[TokenUsage] = None


class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    use_model: Optional[str] = None


class ChatResponse(BaseModel):
    response: ChatMessage
