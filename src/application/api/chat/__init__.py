from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from src.application.api.auth import get_api_auth
from src.modules.llm_modules import LLMModules
from src.schemas.auth import APIAuth
from src.schemas.chat import ChatRequest, ChatResponse
from src.configs.middleware import get_or_create_session_memory, get_session

router = APIRouter()
llm = LLMModules()

@router.post(
    "/",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    raw_request: Request,
    session: dict = Depends(get_session),
    api_auth: APIAuth = Depends(get_api_auth),
):
    session_id = session["session_id"]
    memory = get_or_create_session_memory(session_id)

    response = await llm.chat_completion(
        message=request.message,
        stream=request.stream,
        api_key=api_auth.api_key,
        api_url=api_auth.api_url,
        use_model=api_auth.use_model,
        memory=memory,
    )

    if request.stream:
        return StreamingResponse(response, media_type="text/event-stream")
    else:
        return ChatResponse(response=response)
