# src/schemas/auth.py
from pydantic import BaseModel, validator


class APIAuth(BaseModel):
    api_key: str
    api_url: str
    use_model: str | None = None

    @validator("api_key", "api_url")
    def validate_api_auth(cls, v, values):
        if not v:
            raise ValueError("API key and URL are required")
        return v
