from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uuid
from src.modules.simple_memory import SimpleMemory
from fastapi import Request

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

        # If it's a new session, set cookie in response
        if request.state.new_session:
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=False,
                secure=False,
                samesite="None",
                path="/",
            )

        return response
