import json
from typing import AsyncGenerator, Union, Optional

import httpx
from fastapi import HTTPException
from loguru import logger

from src.adapters.llm_adapter import LLMAdapter
from src.application.rag import get_rag_context
from src.common import LLMConstants, LLMError
from src.configs.configs import config
from src.schemas.chat import ChatMessage, TokenUsage
from src.modules.simple_memory import SimpleMemory


class LLMModules:
    async def chat_completion(
        self,
        message: str,
        timeout: float = 30.0,
        use_model: str | None = None,
        api_key: str | None = None,
        api_url: str | None = None,
        stream: bool = False,
        memory: Optional[SimpleMemory] = None,
    ) -> Union[AsyncGenerator[str, None], ChatMessage]:
        """
        Send a chat completion request to LLM API.
        """

        if api_key is None:
            api_key = config.llm_api_key
        if api_url is None:
            api_url = config.llm_api_url
        if use_model is None:
            use_model = getattr(
                config,
                "llm_model",
                # LLMConstants.DEFAULT_MODEL,
                config.llm_model,
            )

        llm_adapter_instance = LLMAdapter(api_key=api_key, api_url=api_url, memory=memory)
        llm_memory_instance = llm_adapter_instance.memory

        # if use_model not in LLMConstants.AVAILABLE_MODELS:
        #     raise ValueError(
        #         f"Invalid model. Available models: {', '.join(LLMConstants.AVAILABLE_MODELS)}"
        #     )

        kwargs = LLMConstants.kwargs.copy()
        kwargs["model"] = use_model
        kwargs["stream"] = stream

        context = get_rag_context(message)
        logger.info(f"RAG context: {context}")

        message_with_context = (
            f"Context:\n{context}\n\n" f"Question: {message}\n\nAnswer:"
        )

        # Add user message to memory
        llm_memory_instance.add_user_message(message_with_context)
        logger.info(
            f"Current messages in memory: {llm_memory_instance.get_last7_messages()}"
        )

        # Define payload only once
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

                if stream:

                    async def generate_stream():
                        collected_message = ""
                        logger.debug("Starting stream generation")
                        async for line in response.aiter_lines():
                            # logger.debug(f"Raw stream line: {line}")
                            if line.strip():
                                if line.startswith("data: "):
                                    line = line[6:]
                                if line.strip() == "[DONE]":
                                    logger.debug("Stream completed")
                                    break
                                try:
                                    chunk = json.loads(line)
                                    # logger.debug(f"Parsed chunk: {chunk}")
                                    if chunk.get("choices") and chunk[
                                        "choices"
                                    ][0].get("delta", {}).get("content"):
                                        content = chunk["choices"][0]["delta"][
                                            "content"
                                        ]
                                        collected_message += content
                                        # Format as SSE
                                        yield f"data: {content}\n\n"
                                except json.JSONDecodeError as e:
                                    logger.error(
                                        f"JSON decode error: {e} for line: {line}"
                                    )
                                    continue
                        # Add the complete message to memory after streaming is done
                        logger.info(
                            f"Final collected message: {collected_message}"
                        )
                        llm_memory_instance.add_assistant_message(
                            collected_message
                        )

                    return generate_stream()

                # Non-streaming response handling (existing code)
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
