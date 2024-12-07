class LLMError(Exception):
    def __init__(self, message: str, code: int = None, metadata: dict = None):
        self.message = message
        self.code = code
        self.metadata = metadata or {}
        super().__init__(self.message)
