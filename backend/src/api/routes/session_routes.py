from fastapi import APIRouter, HTTPException

from .chat_routes import session_manager
from ...data.redis_manager import redis_client
import uuid

from ...data.session_manager import SessionManager

router = APIRouter()

@router.post("/sessions/create")
async def create_session():
    # session_id = str(uuid.uuid4())
    session_id = session_manager.create_session()
    # redis_client.setex(session_id, 3600, "")  # 1hr expiration
    return {"session_id": session_id}

@router.get("/sessions/{session_id}/validate")
async def validate_session(session_id: str):
    if not redis_client.exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"valid": True}