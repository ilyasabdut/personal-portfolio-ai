from typing import Dict, List


class SimpleMemory:
    def __init__(self):
        self.messages = []

    def add_user_message(self, message: str):
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        self.messages.append({"role": "assistant", "content": message})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def clear_memory(self):
        self.messages = []
