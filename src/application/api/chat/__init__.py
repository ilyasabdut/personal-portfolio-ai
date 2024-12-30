from fastapi import APIRouter, Depends, HTTPException

from src.application.api.auth import get_api_auth
from src.modules.llm_modules import LLMModules
from src.schemas.auth import APIAuth
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
llm = LLMModules()


@router.post(
    "/",
    response_model=ChatResponse,
    dependencies=[Depends(get_api_auth)],
)
async def chat(
    request: ChatRequest,
    api_auth: APIAuth = Depends(get_api_auth),
):
    try:
        response = await llm.chat_completion(
            message=request.message,
            api_key=api_auth.api_key,
            api_url=api_auth.api_url,
        )
        return ChatResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
