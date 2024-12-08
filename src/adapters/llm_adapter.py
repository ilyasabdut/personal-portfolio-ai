from typing import Dict, List

from loguru import logger

from src.common.prompts import Prompts
from src.configs.configs import MoneyTrackerConfig, money_tracker_config
from src.modules.simple_memory import SimpleMemory


class LLMAdapter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLMAdapter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.api_key = money_tracker_config.llm_api_key
            self.api_url = money_tracker_config.llm_api_url

            self.system_prompt = getattr(
                money_tracker_config,
                "llm_system_prompt",
                Prompts.DEFAULT_SYSTEM_PROMPT,
            )

            if not self.api_key:
                raise ValueError("LLM API key not configured")

            self.memory = SimpleMemory()
            logger.info(
                f"Initialized simple memory: {self.memory.get_messages()}"
            )
            self.initialized = True

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": MoneyTrackerConfig.get_server_host(),
            "Content-Type": "application/json",
        }

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build the messages list with system prompt and user messages."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_messages())
        return messages
