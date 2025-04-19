from typing import Dict, List, Optional

from loguru import logger

from src.common.prompts import Prompts
from src.configs.configs import Config, config
from src.modules.simple_memory import SimpleMemory


class LLMAdapter:
    def __init__(self, api_key: str, api_url: str, system_prompt: str = None, memory: Optional[SimpleMemory] = None):
        self.api_key = api_key
        self.api_url = api_url
        self.memory = memory or SimpleMemory([])

        self.system_prompt = getattr(
            config,
            "llm_system_prompt",
            Prompts.DEFAULT_SYSTEM_PROMPT,
        )

        if not self.api_key:
            raise ValueError("LLM API key not configured")

        logger.info(
            f"Initialized simple memory with the last 7 messages: {self.memory.get_last7_messages()}"
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": Config.get_server_host(),
            "Content-Type": "application/json",
        }

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build the messages list with system prompt and user messages."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_last7_messages())
        logger.info(f"Final message list to send: {messages}")

        return messages
