from fastapi import APIRouter, HTTPException
from loguru import logger

from src.adapters import OpenRouterAdapter
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        openrouter = OpenRouterAdapter()
        response = await openrouter.chat_completion(
            message=request.message,
        )
        logger.info(f"OpenRouter response: {response}")
        return ChatResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
