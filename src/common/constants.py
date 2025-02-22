class LLMConstants:
    DEFAULT_MODEL = "meta-llama/llama-3.2-1b-instruct:free"
    AVAILABLE_MODELS = [
        "llama-3.3-70b-specdec",  # Groq
        "llama-3.1-8b-instant",  # Groq
        "meta-llama/llama-3.2-1b-instruct:free",  # OpenRouter
    ]

    kwargs = {
        "temperature": 0.7,
        # "max_tokens": 4096,
        "top_p": 0.8,
        "stop": "```",
        "stream": True,
    }
