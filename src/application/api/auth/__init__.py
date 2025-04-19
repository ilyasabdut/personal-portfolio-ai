import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request,Depends
from fastapi.responses import JSONResponse
from httpx import AsyncClient, HTTPStatusError
from loguru import logger

from src.common.constants import LLMConstants
from src.common.exceptions import LLMError
from src.configs.configs import config
from src.modules.llm_modules import LLMModules
from src.schemas.auth import APIAuth
from src.modules.simple_memory import SimpleMemory
from fastapi.responses import StreamingResponse
from src.configs.middleware import SESSION_MEMORY
import uuid

router = APIRouter()
llm = LLMModules()
# Global session memory map


async def get_api_auth(
    api_key: Optional[str] = Header(None, alias="API_KEY"),
    api_url: Optional[str] = Header(None, alias="API_URL"),
    use_model: Optional[str] = Header(None, alias="LLM_MODEL"),
) -> APIAuth:
    """Validate API credentials and return APIAuth object."""

    # Fallback to env if headers are not provided
    api_key = api_key or config.llm_api_key
    api_url = api_url or config.llm_api_url
    use_model = use_model or config.llm_model

    if not api_key or not api_url:
        raise HTTPException(status_code=400, detail="Missing API credentials")

    response = await test_api_connection(api_key, api_url, use_model)
    if response.status_code == 200:
        return APIAuth(api_key=api_key, api_url=api_url, use_model=use_model)

    raise HTTPException(status_code=401, detail="Invalid API credentials")


async def parse_stream_response(response) -> str:
    """Parse streaming response and concatenate content."""
    full_content = []
    try:
        async for line in response.aiter_lines():
            if not line or line.startswith(
                ":"
            ):  # Skip empty lines and comments
                continue
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])  # Remove "data: " prefix
                    if "choices" in data and data["choices"]:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            content = delta["content"]
                            if content:  # Only append non-empty content
                                full_content.append(content)
                except json.JSONDecodeError:
                    continue

        return "".join(full_content).strip() or "Connected"
    except Exception as e:
        logger.error(f"Error parsing stream: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error parsing streaming response"
        )


async def test_api_connection(
    api_key: str,
    api_url: str,
    use_model: Optional[str] = None,
) -> JSONResponse:
    """Test the API connection with provided credentials."""
    try:
        kwargs = LLMConstants.kwargs.copy()
        kwargs["model"] = use_model or config.llm_model
        # LLMConstants.DEFAULT_MODEL

        payload = {
            **kwargs,
            "messages": [
                {
                    "role": "user",
                    "content": "hello",
                }
            ],
        }

        logger.info(f"Testing API connection: {payload}")
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url.rstrip('/')}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=30.0,
            )

            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            # logger.debug(f"Response body: {response.text}")

            # Handle non-200 responses
            if response.status_code != 200:
                error_message = response.text
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get(
                        "message", response.text
                    )
                except json.JSONDecodeError:
                    pass

                logger.error(f"API returned error: {error_message}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API error: {error_message}",
                )

            # Handle streaming responses
            content_type = response.headers.get("content-type", "")
            logger.info(f"Content-Type: {content_type}")
            if "text/event-stream" in content_type:
                result = await parse_stream_response(response)
                return JSONResponse(
                    content={"message": result}, status_code=200
                )

            # Handle JSON responses
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500, detail="Invalid JSON response from API"
                )

            # Check for API-level errors
            if "error" in data:
                error = data["error"]
                raise LLMError(
                    message=error.get("message", "Unknown error"),
                    code=error.get("code"),
                    metadata=error.get("metadata", {}),
                )

            # Validate response structure
            if "choices" not in data or not data["choices"]:
                logger.error(f"Invalid response structure: {data}")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response structure from API",
                )

            result = data["choices"][0]["message"]["content"]
            logger.info("API connection test successful")

            return JSONResponse(
                content={"message": result},
                status_code=200,
            )

    except asyncio.TimeoutError:
        logger.error("Request timed out")
        raise HTTPException(status_code=504, detail="Request timed out")

    except HTTPStatusError as e:
        logger.error(f"HTTP error: {str(e)}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API error: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process API response: {str(e)}"
        )


@router.post(
    "/test-connection",
    response_model=dict,  # Changed to match the actual response type
    description="Test API connection with provided credentials",
)
async def post_test_api_connection(
    api_key: str,
    api_url: str,
    use_model: Optional[str] = None,
) -> JSONResponse:
    """Test API connection endpoint."""
    return await test_api_connection(api_key, api_url, use_model)

@router.get("/get-session")
async def get_session_endpoint(request: Request):
    session_id = request.state.session_id
    memory = SESSION_MEMORY[session_id]
    return JSONResponse(content={
        "session_id": session_id,
        "messages": memory.get_messages()
    })