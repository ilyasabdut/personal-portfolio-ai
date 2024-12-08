from fastapi import HTTPException
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
)
from langchain_openai import ChatOpenAI
from loguru import logger

from src.common import LLMConstants, LLMError
from src.common.prompts import Prompts
from src.configs.configs import money_tracker_config
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

        if self.model not in LLMConstants.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model. Available models: {', '.join(LLMConstants.AVAILABLE_MODELS)}"
            )

        kwargs = LLMConstants.kwargs

        # Use the OpenAI class to easily switch between different LLM providers
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            base_url=self.api_url,
            **kwargs,
        )

        self.prompt = ChatPromptTemplate.from_template(self.system_prompt)

        self.chain = self.prompt | self.llm

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
        try:
            # Run the chain with memory

            response = await self.chain.ainvoke({"user_message": message})

            # Log the response
            logger.info(f"LLM response: {response}")

            # Check for errors in the response
            if "error" in response:
                error = response["error"]
                raise LLMError(
                    message=error.get("message", "Unknown error"),
                    code=error.get("code"),
                    metadata=error.get("metadata", {}),
                )

            # Extract relevant data from the response
            response_text = response.content
            response_metadata = response.response_metadata
            token_usage = response_metadata.get("token_usage", {})

            # Log the token usage details
            logger.info(f"Token usage: {token_usage}")

            return ChatMessage(
                role="assistant",
                content=response_text,
                usage=TokenUsage(
                    completion_tokens=token_usage.get("completion_tokens", 0),
                    prompt_tokens=token_usage.get("prompt_tokens", 0),
                    total_tokens=token_usage.get("total_tokens", 0),
                    queue_time=token_usage.get("queue_time", 0),
                    prompt_time=token_usage.get("prompt_time", 0),
                    completion_time=token_usage.get("completion_time", 0),
                    total_time=token_usage.get("total_time", 0),
                )
                if token_usage
                else None,
            )

        except LLMError as e:
            logger.error(f"LLM error occurred: {e.message} (code: {e.code})")
            if e.code == 503:  # Service Unavailable
                raise HTTPException(
                    status_code=503,
                    detail=f"Model unavailable: {e.metadata.get('raw', e.message)}",
                )
            raise HTTPException(status_code=500, detail=e.message)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred."
            )
