import os
import httpx
from fastapi import FastAPI, APIRouter
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
async def minimal_chat(request: ChatRequest):
    api_key = os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_API_URL')
    model = os.getenv('LLM_MODEL', 'llama-3.2-11b-vision-preview')

    # Handle both API URLs with and without trailing /v1
    if not api_url.endswith('/v1') and not api_url.endswith('/v1/'):
        api_url = f"{api_url}/v1"

    full_url = f"{api_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": request.message}
        ],
        "stream": request.stream,
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                full_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            response.raise_for_status()

            if request.stream:
                async def generate_stream():
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            yield line + "\n\n"
                return StreamingResponse(generate_stream(), media_type="text/event-stream")
            else:
                data = response.json()
                return ChatResponse(response=data['choices'][0]['message']['content'])
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}")

app.include_router(router)

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
