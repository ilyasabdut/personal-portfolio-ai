from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.api.chat import router as chat_router
from src.configs.configs import MoneyTrackerConfig

app = FastAPI(title="Chat API with OpenRouter")

# Configure CORS
origins = [
    "http://localhost:8000",  # Allow localhost for development
    "https://your-frontend-domain.com",  # Replace with your frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

MoneyTrackerConfig.initiate()

# Create parent API router with prefix
api_router = APIRouter(prefix="/api/v1")

# Add child routers to the parent router
api_router.include_router(chat_router, prefix="/chat")
# Example: api_router.include_router(user_router, prefix="/users")


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat API with OpenRouter"}


# Include the parent router in the app
app.include_router(api_router)
