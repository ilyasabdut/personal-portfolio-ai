from fastapi import APIRouter, HTTPException

from src.adapters import LLMAdapter
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        llm = LLMAdapter()
        response = await llm.chat_completion(
            message=request.message,
        )
        return ChatResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
