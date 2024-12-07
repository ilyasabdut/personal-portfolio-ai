class LLMConstants:
    DEFAULT_MODEL = "llama-3.3-70b-specdec"
    AVAILABLE_MODELS = [
        "llama-3.3-70b-specdec", #Groq
        "meta-llama/llama-3.1-70b-instruct:free", #OpenRouter
    ]

    kwargs = {
        "temperature": 0.0,
        "max_tokens": 4096,
        "top_p": 0.5,
        "stop": "```",
        "stream": False,
    }
