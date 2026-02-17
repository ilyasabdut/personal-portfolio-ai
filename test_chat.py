from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()
router = APIRouter(prefix="/api/v1/chat")

class ChatRequest(BaseModel):
    message: str
    stream: bool = False

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def test_chat(request: ChatRequest, raw_request: Request):
    print(f"Received chat request: {request.message}")
    print(f"Streaming: {request.stream}")

    if request.stream:
        async def generate_stream():
            for word in ["Hello", "!", " How", " can", " I", " assist", " you", " today", "?"]:
                await asyncio.sleep(0.1)
                yield f"data: {word}\n\n"
        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    else:
        return ChatResponse(response="Hello! How can I assist you today?")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
