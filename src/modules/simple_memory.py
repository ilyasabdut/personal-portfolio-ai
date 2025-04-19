from typing import List, Dict


class SimpleMemory:
    def __init__(self, messages: List[Dict[str, str]] = None):
        if messages is None:
            messages = []
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list.")
        
        self.messages = messages

    def add_user_message(self, message: str):
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        self.messages.append({"role": "assistant", "content": message})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def get_last7_messages(self) -> List[Dict[str, str]]:
        return self.messages[-7:]

    def clear_memory(self):
        self.messages.clear()
