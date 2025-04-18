from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.application.api.auth import get_api_auth
from src.modules.llm_modules import LLMModules
from src.schemas.auth import APIAuth
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
llm = LLMModules()


@router.post(
    "/",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    api_auth: APIAuth = Depends(get_api_auth)
):
    response = await llm.chat_completion(
        message=request.message,
        stream=request.stream,
        api_key=api_auth.api_key,
        api_url=api_auth.api_url,
        use_model=api_auth.use_model,
    )

    if request.stream:
        return StreamingResponse(response, media_type="text/event-stream")
    else:
        return ChatResponse(response=response)
