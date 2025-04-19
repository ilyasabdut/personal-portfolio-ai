from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uuid
from src.modules.simple_memory import SimpleMemory
from fastapi import Request
import time

SESSION_MEMORY: dict[str, SimpleMemory] = {}

def generate_session_id():
    return str(uuid.uuid4())

def get_session(request: Request) -> dict:
    session_id = request.state.session_id
    memory = SESSION_MEMORY[session_id]
    return {
        "session_id": session_id,
        "messages": memory.get_messages(),
    }

def get_or_create_session_memory(session_id: str) -> SimpleMemory:
    # This ensures that the session memory exists
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = SimpleMemory(messages=[])
    return SESSION_MEMORY[session_id]

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        session_id = request.cookies.get("session_id")

        if not session_id:
            session_id = generate_session_id()
            request.state.new_session = True
        else:
            request.state.new_session = False

        # Always ensure memory is initialized
        if session_id not in SESSION_MEMORY:
            SESSION_MEMORY[session_id] = SimpleMemory(messages=[])

        request.state.session_id = session_id

        response: Response = await call_next(request)

        if request.state.new_session:
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,  # Ensures the cookie is inaccessible from JavaScript
                secure=True,  # Ensures the cookie is sent only over HTTPS (important for production)
                samesite="Lax",  # Use "Strict" or "Lax" for better security if cross-origin requests are not required
                max_age=60*60*24*7,  # Cookie will last for 1 week (set max-age based on your requirements)
                expires=time.time() + 60*60*24*7,  # Same as max_age, ensures expiration
                path="/",  # Cookie available throughout the entire domain
            )

        return response
