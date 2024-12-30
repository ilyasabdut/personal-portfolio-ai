from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from httpx import AsyncClient, HTTPError
from loguru import logger

from src.common import LLMConstants, LLMError
from src.modules.llm_modules import LLMModules
from src.schemas.auth import APIAuth

router = APIRouter()
llm = LLMModules()


async def get_api_auth(
    api_key: str = Header(..., alias="API_KEY"),
    api_url: str = Header(..., alias="API_URL"),
) -> APIAuth:
    response = await test_api_connection(api_key, api_url)
    if response.status_code == 200:
        return APIAuth(api_key=api_key, api_url=api_url)
    else:
        raise HTTPException(status_code=401, detail="Invalid API credentials")


async def test_api_connection(
    api_key: str,
    api_url: str,
    use_model: str = LLMConstants.DEFAULT_MODEL,
) -> JSONResponse:
    try:
        kwargs = LLMConstants.kwargs
        kwargs["model"] = use_model
        payload = {
            **kwargs,
            "messages": [
                {
                    "role": "user",
                    "content": "Test Connection, if success, return the words Connected only",
                }
            ],
        }

        async with AsyncClient() as client:
            response = await client.post(
                api_url + "/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            data = response.json()
            logger.info(f"API response: {response.json()}")

            if "error" in data:
                error = data["error"]
                raise LLMError(
                    message=error.get("message", "Unknown error"),
                    code=error.get("code"),
                    metadata=error.get("metadata", {}),
                )

            result = data["choices"][0]["message"]["content"]

            return JSONResponse(
                content={"message": result},
                status_code=200,
            )
    except HTTPError as e:
        logger.error(f"Failed to test API connection: {e}")
        raise HTTPException(status_code=401, detail="Invalid API credentials")


@router.post(
    "/test-connection",
    response_model=str,
)
async def post_test_api_connection(
    api_key: str,
    api_url: str,
    use_model: str = None,
):
    return await test_api_connection(api_key, api_url)
