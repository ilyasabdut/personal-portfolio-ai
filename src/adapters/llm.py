from typing import Dict, List

import httpx
from fastapi import HTTPException
from loguru import logger

from src.common import LLMConstants, LLMError
from src.common.prompts import Prompts
from src.configs.configs import MoneyTrackerConfig, money_tracker_config
from src.schemas.chat import ChatMessage, TokenUsage


class LLMAdapter:
    def __init__(self):
        self.api_key = money_tracker_config.llm_api_key
        self.api_url = money_tracker_config.llm_api_url
        self.model = getattr(
            money_tracker_config,
            "llm_model",
            LLMConstants.DEFAULT_MODEL,
        )
        self.system_prompt = getattr(
            money_tracker_config,
            "llm_system_prompt",
            Prompts.DEFAULT_SYSTEM_PROMPT,
        )

        if not self.api_key:
            raise ValueError("LLM API key not configured")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": MoneyTrackerConfig.get_server_host(),
            "Content-Type": "application/json",
        }

    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """Build the messages list with system prompt and user message."""
        return [
            {"role": "user", "content": self.system_prompt.format(user_message=user_message)},
        ]

    async def chat_completion(
        self, message: str, model: str = None, timeout: float = 30.0
    ) -> ChatMessage:
        """
        Send a chat completion request to LLM API.

        Args:
            message: The user's message
            model: Optional model override (defaults to self.model)
            timeout: Request timeout in seconds

        Returns:
            ChatMessage object containing the response and usage statistics

        Raises:
            HTTPException: If the API request fails
            ValueError: If an invalid model is specified
            LLMError: If LLM returns an error response
        """
        use_model = model if model else self.model
        if use_model not in LLMConstants.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model. Available models: {', '.join(LLMConstants.AVAILABLE_MODELS)}"
            )
        kwargs = LLMConstants.kwargs
        kwargs['model'] = use_model

        payload = {
            **kwargs,
            "messages": self._build_messages(message),
        }

        logger.info(f"LLM payload: {payload}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/v1/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"LLM response: {data}")

                if "error" in data:
                    error = data["error"]
                    raise LLMError(
                        message=error.get("message", "Unknown error"),
                        code=error.get("code"),
                        metadata=error.get("metadata", {}),
                    )

                return ChatMessage(
                    role="assistant",
                    content=data["choices"][0]["message"]["content"],
                    usage=TokenUsage(**data["usage"])
                    if "usage" in data
                    else None,
                )

            except httpx.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            except LLMError as e:
                logger.error(f"LLM error: {e.message} (code: {e.code})")
                if e.code == 503:  # Service Unavailable
                    raise HTTPException(
                        status_code=503,
                        detail=f"Model unavailable: {e.metadata.get('raw', e.message)}",
                    )
                raise HTTPException(status_code=500, detail=e.message)
            except Exception as e:
                logger.error(f"Error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
