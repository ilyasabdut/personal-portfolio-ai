from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.configs.middleware import SessionMiddleware
from src.application.api.auth import router as auth_router
from src.application.api.chat import router as chat_router
from src.application.api.upload import router as upload_router
from src.configs.configs import Config
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(title="Chat API with LLM")

# Define middleware array
middleware = [
    {"middleware_class": CORSMiddleware, "allow_origins": ["*"], "allow_credentials": True, "allow_methods": ["*"], "allow_headers": ["*"]},
    {"middleware_class": TrustedHostMiddleware, "allowed_hosts": ["*"]},
    {"middleware_class": SessionMiddleware},
]

for middleware_item in middleware:
    app.add_middleware(middleware_item["middleware_class"], **{k:v for k, v in middleware_item.items() if k != "middleware_class"})

Config.initiate()

# Create parent API router with prefix
api_router = APIRouter(prefix="/api/v1")

# Add child routers to the parent router
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(upload_router, prefix="/upload")

# Example: api_router.include_router(user_router, prefix="/users")


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat API with LLM"}

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# Include the parent router in the app
app.include_router(api_router)
