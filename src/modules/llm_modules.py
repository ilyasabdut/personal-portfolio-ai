import httpx
from fastapi import HTTPException
from loguru import logger

from src.adapters.llm_adapter import LLMAdapter
from src.common import LLMConstants, LLMError
from src.configs.configs import money_tracker_config
from src.schemas.chat import ChatMessage, TokenUsage


class LLMModules:
    async def chat_completion(
        self,
        message: str,
        timeout: float = 30.0,
        use_model: str = None,
        api_key: str = None,
        api_url: str = None,
    ) -> ChatMessage:
        """
        Send a chat completion request to LLM API.
        """

        if api_key is None:
            api_key = money_tracker_config.llm_api_key
        if api_url is None:
            api_url = money_tracker_config.llm_api_url
        if use_model is None:
            use_model = getattr(
                money_tracker_config,
                "llm_model",
                LLMConstants.DEFAULT_MODEL,
            )

        llm_adapter_instance = LLMAdapter(api_key=api_key, api_url=api_url)
        llm_memory_instance = llm_adapter_instance.memory

        if use_model not in LLMConstants.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model. Available models: {', '.join(LLMConstants.AVAILABLE_MODELS)}"
            )
        kwargs = LLMConstants.kwargs
        kwargs["model"] = use_model

        # Add user message to memory
        llm_memory_instance.add_user_message(message)
        logger.info(
            f"Current messages in memory: {llm_memory_instance.get_messages()}"
        )

        payload = {
            **kwargs,
            "messages": llm_adapter_instance._build_messages(),
        }

        logger.info(f"LLM payload: {payload}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{llm_adapter_instance.api_url}/v1/chat/completions",
                    headers=llm_adapter_instance._get_headers(),
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

                # Add assistant message to memory
                llm_adapter_instance.memory.add_assistant_message(
                    data["choices"][0]["message"]["content"]
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
